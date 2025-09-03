from fastapi import APIRouter, Query
from app.db import SessionLocal
from app.models import Transaction

router = APIRouter(tags=["Data Access"])


@router.get("/data/raw", summary="Fetch raw transactions")
def get_raw_data(limit: int = Query(10, description="Max number of rows to return.")):
    """
    Return **raw transaction data** directly from the database.

    Useful for debugging, verifying ingestion, or testing SQL queries.

    **Example:**
    ```bash
    curl "http://localhost:8000/data/raw?limit=5"
    ```
    """
    db = SessionLocal()
    rows = db.query(Transaction).limit(limit).all()
    return {"transactions": [r.as_dict() for r in rows]}
