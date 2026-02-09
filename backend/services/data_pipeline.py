import pandas as pd
import json
from sqlalchemy.orm import Session
from database import Dataset, FinancialRecord


def ingest_file(db: Session, file_path: str, filename: str) -> tuple[int, pd.DataFrame]:
    """Parse an uploaded CSV or Excel file and store it in the database."""
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    dataset = Dataset(
        name=filename.rsplit(".", 1)[0],
        filename=filename,
        row_count=len(df),
        columns=json.dumps(df.columns.tolist()),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    _store_records(db, dataset.id, df)

    return dataset.id, df


def _store_records(db: Session, dataset_id: int, df: pd.DataFrame):
    """Normalize financial data into the records table.

    Supports two formats:
    1. Wide format: period columns with a line_item/category column
    2. Long format: columns for period, category, line_item, amount
    """
    cols_lower = {c.lower(): c for c in df.columns}

    # Check for long format
    if "amount" in cols_lower:
        period_col = cols_lower.get("period", cols_lower.get("date", cols_lower.get("year")))
        category_col = cols_lower.get("category", cols_lower.get("type"))
        item_col = cols_lower.get("line_item", cols_lower.get("item", cols_lower.get("account")))

        if period_col and item_col:
            for _, row in df.iterrows():
                record = FinancialRecord(
                    dataset_id=dataset_id,
                    period=str(row.get(period_col, "")),
                    category=str(row.get(category_col, "")) if category_col else "",
                    line_item=str(row[item_col]),
                    amount=float(row[cols_lower["amount"]]) if pd.notna(row[cols_lower["amount"]]) else 0.0,
                )
                db.add(record)
            db.commit()
            return

    # Wide format: first text column is the line item, numeric columns are periods
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if text_cols and numeric_cols:
        item_col = text_cols[0]
        category_col = text_cols[1] if len(text_cols) > 1 else None

        for _, row in df.iterrows():
            for period_col in numeric_cols:
                record = FinancialRecord(
                    dataset_id=dataset_id,
                    period=str(period_col),
                    category=str(row[category_col]) if category_col else "",
                    line_item=str(row[item_col]),
                    amount=float(row[period_col]) if pd.notna(row[period_col]) else 0.0,
                )
                db.add(record)
        db.commit()


def get_dataset_dataframe(db: Session, dataset_id: int) -> pd.DataFrame:
    """Reconstruct a DataFrame from stored financial records."""
    records = db.query(FinancialRecord).filter(FinancialRecord.dataset_id == dataset_id).all()

    if not records:
        return pd.DataFrame()

    data = [
        {
            "period": r.period,
            "category": r.category,
            "line_item": r.line_item,
            "amount": r.amount,
        }
        for r in records
    ]
    return pd.DataFrame(data)
