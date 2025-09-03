import os
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from app.db import engine
from app.models import Transaction
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

def get_schema():
    insp = inspect(engine)
    columns = insp.get_columns(Transaction.__tablename__)
    col_defs = [f"{col['name']} {col['type']}" for col in columns]
    return f"{Transaction.__tablename__}({', '.join(col_defs)})"

def query_llm(question: str, db: Session):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is missing. Did you create a .env file?"}

    client = OpenAI(api_key=api_key)

    schema = get_schema()

    # Step 1: NL → SQL
    prompt = f"""
    You are a financial analyst.
    Translate the following natural language question into a valid SQL query.
    Database schema: {schema}.
    Only return the SQL query, nothing else.

    Question: {question}
    """

    sql = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    ).choices[0].message.content.strip()

    try:
        rows = db.execute(text(sql)).fetchall()
        result = [dict(r._mapping) for r in rows]  # 👈 JSON serializable

        summary_prompt = f"""
        Question: {question}
        SQL: {sql}
        Result: {result}
        Provide a concise financial insight in plain English.
        """

        answer = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3
        ).choices[0].message.content.strip()

        return {"sql": sql, "result": result, "answer": answer}
    except Exception as e:
        return {"error": str(e), "sql": sql}

