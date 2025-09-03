import json
import os
from app.db import SessionLocal, init_db
from app.models import Transaction

DATA_DIR = "data"


def load_quickbooks(path):
    with open(path) as f:
        raw = json.load(f)

    db = SessionLocal()
    cols = raw["data"]["Columns"]["Column"]
    col_map = {}
    for col in cols:
        if col.get("ColType") == "Money":
            meta = {m["Name"]: m["Value"] for m in col.get("MetaData", [])}
            col_map[col["ColTitle"]] = meta.get("StartDate")

    def process_rows(rows):
        for row in rows:
            # Some rows have nested children
            if "Rows" in row:
                process_rows(row["Rows"]["Row"])
                continue

            if "ColData" not in row:
                continue  # skip headers/totals

            col_data = row["ColData"]
            if not col_data or "value" not in col_data[0]:
                continue

            account = col_data[0]["value"]
            for i, coldata in enumerate(col_data[1:], start=1):
                if "value" not in coldata:
                    continue
                try:
                    amount = float(coldata["value"])
                except ValueError:
                    continue
                col_title = cols[i]["ColTitle"]
                date = col_map.get(col_title)
                t = Transaction(
                    date=date,
                    source="quickbooks",
                    type="revenue" if amount >= 0 else "expense",
                    category=account,
                    amount=abs(amount),
                )
                db.add(t)

    rows = raw["data"]["Rows"]["Row"]
    process_rows(rows)
    db.commit()
    print(f"✅ Loaded QuickBooks data from {path}")


def parse_line_items(line_items, source, type_, date, db):
    for li in line_items:
        t = Transaction(
            date=date,
            source=source,
            type=type_,
            category=li["name"],
            amount=float(li.get("value", 0)),
        )
        db.add(t)
        if "line_items" in li and li["line_items"]:
            parse_line_items(li["line_items"], source, type_, date, db)


def load_rootfi(path):
    with open(path) as f:
        raw = json.load(f)

    db = SessionLocal()
    for report in raw["data"]:
        date = report.get("period_end")
        # Revenue
        for rev in report.get("revenue", []):
            parse_line_items([rev], "rootfi", "revenue", date, db)
        # COGS / expenses
        for cogs in report.get("cost_of_goods_sold", []):
            parse_line_items([cogs], "rootfi", "expense", date, db)
        for exp in report.get("operating_expenses", []):
            parse_line_items([exp], "rootfi", "expense", date, db)
    db.commit()
    print(f"✅ Loaded Rootfi data from {path}")


if __name__ == "__main__":
    init_db()
    load_quickbooks(os.path.join(DATA_DIR, "data_set_1.json"))
    load_rootfi(os.path.join(DATA_DIR, "data_set_2.json"))
    print("🎉 All data loaded successfully")
