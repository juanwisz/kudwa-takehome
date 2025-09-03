# scripts/load_data.py
import os
import json
import logging
from typing import Any, Dict, List, Optional

from app.db import SessionLocal, init_db
from app.models import Transaction

DATA_DIR = "data"

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# --- Helpers ---
def safe_float(val: Any) -> Optional[float]:
    """Try to parse a float, return None if invalid."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# --- QuickBooks Loader ---
def load_quickbooks(path: str, db):
    logger.info(f"Loading QuickBooks data from {path}")

    with open(path) as f:
        raw = json.load(f)

    cols = raw["data"]["Columns"]["Column"]
    # Map col titles ("Jan 2020") to StartDate ("2020-01-01")
    col_map = {}
    for col in cols:
        if col.get("ColType") == "Money":
            meta = {m["Name"]: m["Value"] for m in col.get("MetaData", [])}
            col_map[col["ColTitle"]] = meta.get("StartDate")

    def process_rows(rows: List[Dict]):
        for row in rows:
            if "Rows" in row:  # Nested children
                process_rows(row["Rows"]["Row"])
                continue

            if "ColData" not in row:
                continue  # Skip headers/totals

            col_data = row["ColData"]
            if not col_data or "value" not in col_data[0]:
                continue

            account = col_data[0]["value"]
            for i, coldata in enumerate(col_data[1:], start=1):
                amount = safe_float(coldata.get("value"))
                if amount is None:
                    continue

                col_title = cols[i]["ColTitle"]
                date = col_map.get(col_title)
                t_type = "revenue" if amount >= 0 else "expense"

                tx = Transaction(
                    date=date,
                    source="quickbooks",
                    type=t_type,
                    category=account,
                    amount=abs(amount),
                )
                db.add(tx)

    rows = raw["data"]["Rows"]["Row"]
    process_rows(rows)
    db.commit()
    logger.info("✅ QuickBooks data loaded successfully")


# --- Rootfi Loader ---
def load_rootfi(path: str, db):
    logger.info(f"Loading Rootfi data from {path}")

    with open(path) as f:
        raw = json.load(f)

    for entry in raw["data"]:
        date = entry.get("period_end")

        def process_items(items: List[Dict], t_type: str):
            for item in items:
                amount = safe_float(item.get("value"))
                if amount is None or amount == 0:
                    continue
                tx = Transaction(
                    date=date,
                    source="rootfi",
                    type=t_type,
                    category=item.get("name", "unknown"),
                    amount=abs(amount),
                )
                db.add(tx)

                # Recurse into nested line_items
                if "line_items" in item and isinstance(item["line_items"], list):
                    process_items(item["line_items"], t_type)

        process_items(entry.get("revenue", []), "revenue")
        process_items(entry.get("cost_of_goods_sold", []), "expense")
        process_items(entry.get("operating_expenses", []), "expense")
        process_items(entry.get("other_expenses", []), "expense")
        process_items(entry.get("net_income", []), "profit")

    db.commit()
    logger.info("✅ Rootfi data loaded successfully")


# --- Entrypoint ---
def main():
    logger.info("Initializing database...")
    init_db()
    db = SessionLocal()

    quickbooks_path = os.path.join(DATA_DIR, "data_set_1.json")
    rootfi_path = os.path.join(DATA_DIR, "data_set_2.json")

    if os.path.exists(quickbooks_path):
        load_quickbooks(quickbooks_path, db)
    else:
        logger.warning("QuickBooks dataset not found")

    if os.path.exists(rootfi_path):
        load_rootfi(rootfi_path, db)
    else:
        logger.warning("Rootfi dataset not found")

    db.close()
    logger.info("🎉 Data loading complete!")


if __name__ == "__main__":
    main()
