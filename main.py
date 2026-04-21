import uvicorn
from fastapi import FastAPI

from src.presentation.lifespan import lifespan
from src.presentation.middleware.request_id_middleware import RequestIdMiddleware
from src.presentation.routes.callbacks import router as callbacks_router
from src.presentation.routes.orders import router as orders_router
from src.utils.logs_endpoint import download_logs

app = FastAPI(
    lifespan=lifespan,
    title="Capashino Order Service",
    description="Event-driven order management service with clean architecture",
)

app.add_middleware(RequestIdMiddleware)

app.include_router(orders_router)
app.include_router(callbacks_router)


@app.get("/logs")(download_logs)
@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    """Start the application with hot-reload enabled for development."""
    print("Starting Order Service in development mode with reload=True.")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True,
        log_level="info",
    )

# run tests 6
