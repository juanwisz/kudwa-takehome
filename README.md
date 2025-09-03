# Kudwa Financial AI System

This system integrates multiple financial data sources into a unified backend and provides AI-powered natural language analysis.

---

## Setup Instructions

### 1. Clone Repository
```bash
git clone <repo_url>
cd <repo>
```

### 2. Create Virtual Environment and Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory with your OpenAI key:
```text
OPENAI_API_KEY=sk-xxxx
```

### 4. Initialize Database
```bash
make load_data
```
This will parse the provided datasets (`data_set_1.json` and `data_set_2.json`) and populate `financial.db`.

### 5. Run the API
```bash
make run
```
Or with Docker:
```bash
docker build -t kudwa-ai .
docker run -p 8000:8000 kudwa-ai
```

---

## Database Initialization

- Database: SQLite (`financial.db`)  
- Schema includes:
  - `transactions` table: stores normalized financial transactions
  - `query_logs` table: stores user queries, SQL, reports, and results

Initialization is handled automatically by `app/db.py` on startup, and `scripts/load_data.py` populates initial data.

---

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Fetch Raw Data
```bash
curl "http://localhost:8000/data/raw?limit=5"
```

### Natural Language Query
```bash
curl "http://localhost:8000/query?q=What was the total profit in Q1?"
```

**Response Example:**
```json
{
  "question": "What was the total profit in Q1?",
  "report": "## Profit Report\n- Q1 profit totaled $1,245,000\n- Driven by consulting income\n- Expenses remained stable"
}
```

### Forecast Plot
```bash
curl -o forecast.png "http://localhost:8000/plot/forecast?horizon=6"
```
This generates a PNG chart with historical revenue and forecasted values.

### Interactive API Documentation

This project uses FastAPI, which provides interactive documentation automatically:

- **Swagger UI** (try out endpoints directly):  
  [https://kudwa-takehome.onrender.com/docs](https://kudwa-takehome.onrender.com/docs)

- **ReDoc** (clean reference-style docs):  
  [https://kudwa-takehome.onrender.com/redoc](https://kudwa-takehome.onrender.com/redoc)

These are enabled by default when you run the server locally or deploy with Docker/Render.

---

## Deployment

- Configured for Render using `render.yaml`
- Auto-builds Docker container on push
- API available at `https://kudwa-takehome.onrender.com/`