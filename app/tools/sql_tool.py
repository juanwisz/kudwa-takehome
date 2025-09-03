from langchain_core.tools import tool
from sqlalchemy import text
from app.db import SessionLocal

@tool
def sql_query(sql: str) -> list[dict]:
    """Execute a read-only SQL query on the `transactions` table and return results as a list of dicts."""
    db = SessionLocal()
    try:
        rows = db.execute(text(sql)).fetchall()
        return [dict(r._mapping) for r in rows]
    finally:
        db.close()
