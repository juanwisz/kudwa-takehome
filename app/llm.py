import os
import json
from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

from app.db import engine, SessionLocal
from app.models import Transaction, QueryLog
from app.prompts import build_agent_prompt
from app.tools.sql_tool import sql_query
from app.tools.forecast_tool import forecast_arima
from app.logger import logger

load_dotenv()


def get_schema() -> str:
    """Inspect the DB and return schema definition for transactions table."""
    insp = inspect(engine)
    cols = insp.get_columns(Transaction.__tablename__)
    col_defs = [f"{c['name']} {c['type']}" for c in cols]
    return f"{Transaction.__tablename__}({', '.join(col_defs)})"


def log_query(question: str, sql: str, tool: str, result: dict, report: str):
    """Persist query execution into QueryLog table."""
    db = SessionLocal()
    try:
        entry = QueryLog(
            question=question,
            sql=sql,
            tool=tool,
            result=json.dumps(result) if result else None,
            report=report,
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.warning("Failed to log query: %s", str(e))
        db.rollback()
    finally:
        db.close()


def query_agent(question: str, db: Session):
    """Main entrypoint: run user question through LLM agent and persist results."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY is missing"
        logger.error(msg)
        return {"error": msg}

    # Build context-aware system prompt
    schema = get_schema()
    system_prompt = build_agent_prompt(schema)

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=api_key,
    )

    # Register tools available to the agent
    tools = [sql_query, forecast_arima]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs={"system_message": system_prompt},
    )

    try:
        report = agent.run(question)
        logger.info("QUESTION=%s | REPORT=%s", question, report[:200])

        # Collect minimal metadata for logging
        sql = getattr(sql_query, "last_sql", None) or ""
        result = getattr(sql_query, "last_result", {}) or {}
        tool_used = "forecast_arima" if "forecast" in question.lower() else "sql_query"

        log_query(question, sql, tool_used, result, report)

        return {"question": question, "report": report}
    except Exception as e:
        err_msg = f"Agent failed: {str(e)}"
        logger.error(err_msg)
        log_query(question, "", "agent", {}, f"ERROR: {str(e)}")
        return {"error": str(e)}
