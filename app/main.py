from fastapi import FastAPI, Query
from .db import SessionLocal, init_db
from .models import Transaction
from .llm import query_llm   # <-- make sure this import is here

app = FastAPI(title="Kudwa Financial AI System")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Hello from Kudwa Financial AI System"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/data/raw")
def get_data(limit: int = 20):
    db = SessionLocal()
    records = db.query(Transaction).limit(limit).all()
    return {"transactions": [r.as_dict() for r in records]}

@app.get("/data/query")
def natural_query(q: str = Query(..., description="Natural language question")):
    db = SessionLocal()
    return query_llm(q, db)
