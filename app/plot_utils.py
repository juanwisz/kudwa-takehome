# app/plot_utils.py
import io
import pandas as pd
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from app.db import SessionLocal
from statsmodels.tsa.arima.model import ARIMA


def generate_forecast_plot(horizon: int = 6):
    """
    Generate a PNG chart showing historical monthly revenue
    and an ARIMA forecast for the requested horizon.
    """

    # --- Query revenue data ---
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT date, amount FROM transactions WHERE type='revenue'")
        ).fetchall()
        df = pd.DataFrame([dict(r._mapping) for r in rows])
    finally:
        db.close()

    # --- Handle empty dataset ---
    if df.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No revenue data available", ha="center", va="center")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    # --- Prepare time series ---
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby(pd.Grouper(key="date", freq="M")).sum().sort_index()
    df = df.asfreq("M", fill_value=0)
    series = df["amount"].astype(float)

    # --- Forecast with ARIMA ---
    try:
        model = ARIMA(series, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=horizon)
    except Exception as e:
        forecast = pd.Series([], dtype=float)

    # --- Plot history + forecast ---
    fig, ax = plt.subplots()
    series.plot(ax=ax, label="Historical", marker="o")
    if not forecast.empty:
        forecast.index = pd.date_range(
            start=series.index[-1] + pd.offsets.MonthEnd(),
            periods=horizon,
            freq="M"
        )
        forecast.plot(ax=ax, label="Forecast", linestyle="--", marker="x")

    ax.set_title(f"Revenue Forecast (next {horizon} months)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (USD)")
    ax.legend()

    # --- Return PNG ---
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
