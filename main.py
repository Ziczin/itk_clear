from fastapi import FastAPI
import uvicorn

from src.presentation.lifespan import lifespan
from src.presentation.routes.orders import order_router


app = FastAPI(
    lifespan=lifespan,
    title="Capashino Order Service",
    description="Event-driven order management service with clean architecture",
)

app.include_router(order_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


#
if __name__ == "__main__":
    """Start the application with hot-reload enabled for development."""
    print("Starting Order Service in development mode with reload=True.")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
