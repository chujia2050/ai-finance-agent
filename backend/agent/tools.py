"""LangChain tools for the financial analysis agent."""

from langchain_core.tools import tool
from sqlalchemy.orm import Session
from services.data_pipeline import get_dataset_dataframe
from services import financial_analysis as fa


def create_tools(db: Session, dataset_id: int):
    """Create LangChain tools bound to a specific dataset."""

    df = get_dataset_dataframe(db, dataset_id)

    @tool
    def query_financial_data(query: str) -> str:
        """Query the financial dataset. You can ask for specific line items,
        periods, or categories. Supports queries like:
        - 'revenue for all periods'
        - 'all items in 2024-Q1'
        - 'operating expenses by period'

        Args:
            query: A natural language description of what data to retrieve.
        """
        q = query.lower()
        result = df.copy()

        # Filter by period
        for period in df["period"].unique():
            if str(period).lower() in q:
                result = result[result["period"] == period]
                break

        # Filter by category
        for cat in df["category"].unique():
            if cat and cat.lower() in q:
                result = result[result["category"] == cat]
                break

        # Filter by line item keyword
        keywords = ["revenue", "income", "expense", "cost", "profit", "asset",
                     "liability", "equity", "cash", "debt", "ebitda", "tax"]
        for kw in keywords:
            if kw in q:
                result = result[result["line_item"].str.lower().str.contains(kw)]
                break

        if result.empty:
            return f"No matching data found for query: {query}. Available line items: {df['line_item'].unique().tolist()[:20]}"

        return result.to_string(index=False)

    @tool
    def calculate_financial_ratios() -> str:
        """Calculate key financial ratios including profitability ratios
        (gross margin, operating margin, net margin), liquidity ratios
        (current ratio, quick ratio), and leverage ratios (debt-to-equity,
        return on equity). Uses the most recent period's data."""
        ratios = fa.compute_ratios(df)
        if not ratios:
            return "Could not compute ratios. Check that the dataset contains standard financial line items."

        lines = [f"Financial Ratios (Period: {ratios.pop('period', 'N/A')}):\n"]
        ratio_labels = {
            "gross_margin": "Gross Margin",
            "operating_margin": "Operating Margin",
            "net_margin": "Net Margin",
            "ebitda_margin": "EBITDA Margin",
            "current_ratio": "Current Ratio",
            "quick_ratio": "Quick Ratio",
            "cash_ratio": "Cash Ratio",
            "debt_to_equity": "Debt to Equity",
            "debt_to_assets": "Debt to Assets",
            "return_on_equity": "Return on Equity (ROE)",
            "return_on_assets": "Return on Assets (ROA)",
        }
        for key, label in ratio_labels.items():
            if key in ratios:
                unit = "%" if "margin" in key or "return" in key else "x"
                lines.append(f"  {label}: {ratios[key]}{unit}")

        return "\n".join(lines)

    @tool
    def analyze_trends() -> str:
        """Analyze period-over-period trends for all financial line items.
        Shows which items are increasing, decreasing, or stable, along with
        the average percentage change."""
        trends = fa.compute_trends(df)
        if not trends:
            return "Not enough periods to analyze trends (need at least 2)."

        lines = ["Trend Analysis:\n"]
        for t in trends[:15]:
            arrow = "↑" if t["direction"] == "increasing" else "↓" if t["direction"] == "decreasing" else "→"
            lines.append(
                f"  {arrow} {t['line_item']}: {t['direction']} "
                f"(avg {t['avg_change_pct']:+.1f}% per period)"
            )
            for p, v in t["values_by_period"].items():
                lines.append(f"      {p}: {v:,.2f}")

        return "\n".join(lines)

    @tool
    def detect_anomalies() -> str:
        """Detect statistical anomalies in the financial data. Identifies
        values that deviate significantly from the mean for each line item.
        Flags items that are more than 1.5 standard deviations from average."""
        anomalies = fa.detect_anomalies(df)
        if not anomalies:
            return "No significant anomalies detected in the financial data."

        lines = ["Anomaly Detection Results:\n"]
        for a in anomalies[:10]:
            lines.append(
                f"  [{a['severity'].upper()}] {a['description']}\n"
                f"      Amount: {a['amount']:,.2f} | "
                f"Mean: {a['mean']:,.2f} | Z-Score: {a['z_score']}"
            )

        return "\n".join(lines)

    @tool
    def compare_periods(period1: str = "", period2: str = "") -> str:
        """Compare financial data between two periods side by side.
        Shows absolute and percentage changes for each line item.
        If periods are not specified, compares the two most recent periods.

        Args:
            period1: The first/earlier period to compare (e.g., '2023-Q3').
            period2: The second/later period to compare (e.g., '2024-Q1').
        """
        result = fa.compare_periods(df, period1 or None, period2 or None)

        if "error" in result:
            return result["error"]

        lines = [f"Period Comparison: {result['period_1']} vs {result['period_2']}\n"]
        lines.append(f"{'Line Item':<30} {'Period 1':>15} {'Period 2':>15} {'Change':>12} {'% Change':>10}")
        lines.append("-" * 85)

        for item in result["items"][:20]:
            pct = f"{item['percent_change']:+.1f}%" if item["percent_change"] is not None else "N/A"
            lines.append(
                f"{item['line_item']:<30} "
                f"{item['period_1_value']:>15,.2f} "
                f"{item['period_2_value']:>15,.2f} "
                f"{item['absolute_change']:>12,.2f} "
                f"{pct:>10}"
            )

        return "\n".join(lines)

    @tool
    def get_data_summary() -> str:
        """Get a high-level summary of the financial dataset including
        available periods, categories, line item count, and totals by period."""
        summary = fa.compute_summary(df)
        lines = [
            "Dataset Summary:",
            f"  Periods: {', '.join(str(p) for p in summary['periods'])}",
            f"  Categories: {', '.join(summary['categories']) if summary['categories'] else 'N/A'}",
            f"  Line Items: {summary['line_item_count']}",
            "\n  Totals by Period:",
        ]
        for period, total in summary["total_by_period"].items():
            lines.append(f"    {period}: {total:,.2f}")

        return "\n".join(lines)

    return [
        query_financial_data,
        calculate_financial_ratios,
        analyze_trends,
        detect_anomalies,
        compare_periods,
        get_data_summary,
    ]
