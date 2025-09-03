from app.db import SessionLocal, init_db
from app.llm import query_agent
from app.logger import logger

SAMPLE_QUERIES = [
    "What was the total profit in Q1?",
    "Show me revenue trends for 2024",
    "Which expense category had the highest increase this year?",
    "Compare Q1 and Q2 performance"
]

def main():
    init_db()
    db = SessionLocal()

    logger.info("🚀 Running sample validation queries")
    for q in SAMPLE_QUERIES:
        logger.info(">>> Running: %s", q)
        result = query_agent(q, db)
        print("\n>>>", q)
        print(result)
        print("-" * 80)

    db.close()
    logger.info("✅ Sample queries complete")

if __name__ == "__main__":
    main()
