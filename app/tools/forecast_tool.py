from langchain_core.tools import tool
from sqlalchemy import text
from app.db import SessionLocal
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


@tool
def forecast_arima(sql: str, horizon: int, target: str) -> dict:
    """Fetch data with SQL and run an ARIMA forecast.

    Args:
        sql: SQL query with a time column and a numeric target column.
        horizon: Number of future periods to predict.
        target: The column name to forecast (e.g. 'revenue').
    """
    db = SessionLocal()
    try:
        rows = db.execute(text(sql)).fetchall()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
    finally:
        db.close()

    if df.empty:
        return {"error": "No data returned for forecast"}

    # Assume first column is date/time
    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])

    # --- FIX: aggregate duplicates by month ---
    df = df.groupby(pd.Grouper(key=date_col, freq="M")).sum().sort_index()

    # Ensure continuous monthly frequency
    df = df.asfreq("M", fill_value=0)

    # Forecast target series
    if target not in df.columns:
        return {"error": f"Target column '{target}' not found in data"}

    series = df[target].astype(float)

    try:
        model = ARIMA(series, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=horizon)
    except Exception as e:
        return {"error": f"ARIMA failed: {str(e)}"}

    history = series.tail(6).to_dict()
    future = {f"t+{i+1}": float(val) for i, val in enumerate(forecast)}

    return {"history": history, "forecast": future}
