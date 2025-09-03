from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.llm import query_agent

router = APIRouter(tags=["AI Querying"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/query", summary="Ask a financial question (AI-powered)")
def query_endpoint(
    q: str = Query(
        ...,
        description=(
            "A natural language financial question.\n\n"
            "Examples:\n"
            "- `What was the total profit in Q1?`\n"
            "- `Show me revenue trends for 2024`\n"
            "- `Which expense category had the highest increase this year?`\n"
            "- `Forecast revenue for the next 3 months`"
        ),
    ),
    db: Session = Depends(get_db),
):
    """
    Use this endpoint to query financial data **in natural language**.

    The AI agent will:
    1. Translate your question into a safe SQL query.
    2. Optionally apply forecasting or analysis tools.
    3. Return a clear, narrative insight **plus** structured results.

    **Response format:**
    ```json
    {
      "question": "Forecast revenue for the next 3 months",
      "report": "# Revenue Forecast Report ...",
    }
    ```
    """
    return query_agent(q, db)
