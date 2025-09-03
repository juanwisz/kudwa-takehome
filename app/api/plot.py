from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.plot_utils import generate_forecast_plot

router = APIRouter(tags=["Forecasting & Visualization"])


@router.get(
    "/plot/forecast",
    summary="Generate a revenue forecast plot (PNG)",
    response_class=StreamingResponse,
)
def forecast_plot(
    horizon: int = Query(
        6,
        description="Number of months to forecast forward (default: 6)."
    ),
):
    """
    Returns a **PNG chart** with historical revenue and a forecast for the
    requested number of future months.

    Use this to quickly **visualize trends** without running a natural
    language query.

    **Example:**
    ```bash
    curl -o forecast.png "http://localhost:8000/plot/forecast?horizon=6"
    ```
    """
    return generate_forecast_plot(horizon)
