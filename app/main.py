from fastapi import FastAPI
from app.db import init_db
from app.api import health, data, query, plot, logs

app = FastAPI(title="Kudwa Financial AI System")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Hello from Kudwa Financial AI System"}

# Mount routers
app.include_router(health.router, prefix="")      # /health
app.include_router(data.router, prefix="/data")  # /data/raw etc.
app.include_router(query.router, prefix="")      # /query (hero feature)
app.include_router(plot.router, prefix="")  # expose /plot/forecast
app.include_router(logs.router, prefix="")
