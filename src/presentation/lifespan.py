import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.bootstrap.database import apply_migrations
from src.infrastructure.bootstrap.kafka import initialize_kafka_producer
from src.infrastructure.bootstrap.background import start_background_workers
from src.infrastructure.bootstrap.monitoring import initialize_sentry_monitoring
from src.utils.context_vars import logger, set_request_id, clear_request_id


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Coordinate application startup sequence and graceful shutdown procedures."""
    request_id = set_request_id("lifespan-context")
    try:
        logger.info("Initializing application components")

        try:
            await initialize_sentry_monitoring()

            await apply_migrations()

            application.state.http_session = aiohttp.ClientSession()
            logger.info("HTTP client session established")

            application.state.kafka_producer = await initialize_kafka_producer()

            await start_background_workers(application, application.state.http_session)

            yield

            logger.info("Initiating graceful shutdown sequence")
            if hasattr(application.state, "outbox_task"):
                application.state.outbox_task.cancel()
            if hasattr(application.state, "shipment_task"):
                application.state.shipment_task.cancel()
            await application.state.http_session.close()
            if hasattr(application.state, "kafka_producer"):
                await application.state.kafka_producer.stop()
            logger.info("Application shutdown completed successfully")

        except Exception as exception:
            logger.error(
                "Critical initialization failure detected", error=str(exception)
            )
            raise
    finally:
        clear_request_id()
