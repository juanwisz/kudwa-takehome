from fastapi import FastAPI

app = FastAPI(title="Kudwa Financial AI System")

@app.get("/")
def root():
    return {"message": "Hello from Kudwa Financial AI System"}

@app.get("/health")
def health():
    return {"status": "ok"}
