from fastapi import APIRouter

router = APIRouter(tags=["System Health"])


@router.get("/health", summary="Health check")
def health_check():
    """
    Quick **health check** endpoint to verify the service is running.

    **Example:**
    ```bash
    curl http://localhost:8000/health
    ```

    **Response:**
    ```json
    {"status": "ok"}
    ```
    """
    return {"status": "ok"}
