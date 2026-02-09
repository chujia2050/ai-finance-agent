import pandas as pd
import numpy as np


def compute_summary(df: pd.DataFrame) -> dict:
    """Compute high-level summary statistics for the financial dataset."""
    periods = sorted(df["period"].unique().tolist())
    categories = df["category"].unique().tolist()
    line_items = df["line_item"].unique().tolist()
    total_by_period = df.groupby("period")["amount"].sum().to_dict()

    return {
        "periods": periods,
        "categories": [c for c in categories if c],
        "line_item_count": len(line_items),
        "total_by_period": {str(k): round(v, 2) for k, v in total_by_period.items()},
    }


def compute_ratios(df: pd.DataFrame) -> dict:
    """Calculate key financial ratios from the data.

    Attempts to identify common financial line items and compute ratios.
    """
    ratios = {}
    item_map = _build_item_map(df)

    latest_period = sorted(df["period"].unique())[-1]
    period_data = df[df["period"] == latest_period]
    pm = _build_item_map(period_data)

    # Profitability ratios
    revenue = pm.get("revenue", pm.get("total_revenue", pm.get("net_revenue", pm.get("sales", 0))))
    cogs = pm.get("cogs", pm.get("cost_of_goods_sold", pm.get("cost_of_revenue", 0)))
    net_income = pm.get("net_income", pm.get("net_profit", pm.get("net_earnings", 0)))
    operating_income = pm.get("operating_income", pm.get("operating_profit", pm.get("ebit", 0)))
    gross_profit = pm.get("gross_profit", revenue - cogs if revenue and cogs else 0)
    ebitda = pm.get("ebitda", 0)

    if revenue:
        ratios["gross_margin"] = round((gross_profit / revenue) * 100, 2) if gross_profit else None
        ratios["operating_margin"] = round((operating_income / revenue) * 100, 2) if operating_income else None
        ratios["net_margin"] = round((net_income / revenue) * 100, 2) if net_income else None
        ratios["ebitda_margin"] = round((ebitda / revenue) * 100, 2) if ebitda else None

    # Liquidity ratios
    current_assets = pm.get("current_assets", pm.get("total_current_assets", 0))
    current_liabilities = pm.get("current_liabilities", pm.get("total_current_liabilities", 0))
    cash = pm.get("cash", pm.get("cash_and_equivalents", pm.get("cash_and_cash_equivalents", 0)))
    inventory = pm.get("inventory", pm.get("inventories", 0))

    if current_liabilities:
        ratios["current_ratio"] = round(current_assets / current_liabilities, 2) if current_assets else None
        ratios["quick_ratio"] = (
            round((current_assets - inventory) / current_liabilities, 2)
            if current_assets
            else None
        )
        ratios["cash_ratio"] = round(cash / current_liabilities, 2) if cash else None

    # Leverage ratios
    total_assets = pm.get("total_assets", 0)
    total_liabilities = pm.get("total_liabilities", 0)
    total_equity = pm.get("total_equity", pm.get("shareholders_equity", pm.get("total_shareholders_equity", 0)))

    if total_equity:
        ratios["debt_to_equity"] = round(total_liabilities / total_equity, 2) if total_liabilities else None
        ratios["return_on_equity"] = round((net_income / total_equity) * 100, 2) if net_income else None

    if total_assets:
        ratios["debt_to_assets"] = round(total_liabilities / total_assets, 2) if total_liabilities else None
        ratios["return_on_assets"] = round((net_income / total_assets) * 100, 2) if net_income else None

    # Filter out None values
    ratios = {k: v for k, v in ratios.items() if v is not None}
    ratios["period"] = latest_period

    return ratios


def compute_trends(df: pd.DataFrame) -> list[dict]:
    """Analyze period-over-period trends for each line item."""
    trends = []
    periods = sorted(df["period"].unique())

    if len(periods) < 2:
        return trends

    for item in df["line_item"].unique():
        item_data = df[df["line_item"] == item].sort_values("period")
        amounts = item_data.set_index("period")["amount"]

        if len(amounts) < 2:
            continue

        values = [amounts.get(p, 0) for p in periods]
        changes = []
        for i in range(1, len(values)):
            if values[i - 1] != 0:
                pct = round(((values[i] - values[i - 1]) / abs(values[i - 1])) * 100, 2)
            else:
                pct = None
            changes.append({"from": periods[i - 1], "to": periods[i], "change_pct": pct})

        avg_change = np.mean([c["change_pct"] for c in changes if c["change_pct"] is not None])
        direction = "increasing" if avg_change > 2 else "decreasing" if avg_change < -2 else "stable"

        trends.append({
            "line_item": item,
            "category": item_data.iloc[0]["category"],
            "values_by_period": {str(p): round(v, 2) for p, v in zip(periods, values)},
            "period_changes": changes,
            "avg_change_pct": round(float(avg_change), 2) if not np.isnan(avg_change) else 0,
            "direction": direction,
        })

    return sorted(trends, key=lambda t: abs(t["avg_change_pct"]), reverse=True)


def detect_anomalies(df: pd.DataFrame) -> list[dict]:
    """Detect anomalies in the financial data using statistical methods."""
    anomalies = []
    periods = sorted(df["period"].unique())

    if len(periods) < 3:
        return anomalies

    for item in df["line_item"].unique():
        item_data = df[df["line_item"] == item].sort_values("period")
        amounts = item_data["amount"].values

        if len(amounts) < 3:
            continue

        mean = np.mean(amounts)
        std = np.std(amounts)

        if std == 0:
            continue

        for _, row in item_data.iterrows():
            z_score = (row["amount"] - mean) / std
            if abs(z_score) > 1.5:
                anomalies.append({
                    "line_item": row["line_item"],
                    "category": row["category"],
                    "period": row["period"],
                    "amount": round(row["amount"], 2),
                    "mean": round(mean, 2),
                    "std_dev": round(std, 2),
                    "z_score": round(z_score, 2),
                    "severity": "high" if abs(z_score) > 2.5 else "medium",
                    "description": (
                        f"{row['line_item']} in {row['period']} "
                        f"({'above' if z_score > 0 else 'below'} average by "
                        f"{abs(round(z_score, 1))} std deviations)"
                    ),
                })

    return sorted(anomalies, key=lambda a: abs(a["z_score"]), reverse=True)


def compare_periods(df: pd.DataFrame, period1: str | None = None, period2: str | None = None) -> dict:
    """Compare two periods side by side."""
    periods = sorted(df["period"].unique())

    if len(periods) < 2:
        return {"error": "Need at least 2 periods for comparison"}

    p1 = period1 or periods[-2]
    p2 = period2 or periods[-1]

    df1 = df[df["period"] == p1].set_index("line_item")["amount"]
    df2 = df[df["period"] == p2].set_index("line_item")["amount"]

    all_items = sorted(set(df1.index) | set(df2.index))
    comparison = []

    for item in all_items:
        v1 = df1.get(item, 0)
        v2 = df2.get(item, 0)
        change = v2 - v1
        change_pct = round((change / abs(v1)) * 100, 2) if v1 != 0 else None

        comparison.append({
            "line_item": item,
            "period_1_value": round(v1, 2),
            "period_2_value": round(v2, 2),
            "absolute_change": round(change, 2),
            "percent_change": change_pct,
        })

    return {
        "period_1": p1,
        "period_2": p2,
        "items": sorted(comparison, key=lambda x: abs(x["absolute_change"]), reverse=True),
    }


def _build_item_map(df: pd.DataFrame) -> dict:
    """Build a mapping of normalized line item names to their amounts."""
    item_map = {}
    for _, row in df.iterrows():
        key = row["line_item"].lower().strip().replace(" ", "_").replace("-", "_")
        item_map[key] = row["amount"]
    return item_map
