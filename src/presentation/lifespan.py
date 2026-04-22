from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from src.config import settings
from src.infrastructure.bootstrap.background import start_background_workers
from src.infrastructure.bootstrap.database import apply_migrations
from src.infrastructure.bootstrap.kafka import initialize_kafka_producer
from src.infrastructure.bootstrap.monitoring import initialize_sentry_monitoring
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Coordinate application startup sequence and graceful shutdown procedures."""
    logger.info("LIFESPAN | Initializing application components")
    logger.warning(str(settings.CAPASHINO_API_KEY))
    try:
        await initialize_sentry_monitoring()

        await apply_migrations()

        application.state.http_session = aiohttp.ClientSession()
        logger.info("LIFESPAN | HTTP client session established")

        application.state.kafka_producer = await initialize_kafka_producer()

        await start_background_workers(application, application.state.http_session)

        yield

        logger.info("LIFESPAN | Initiating graceful shutdown sequence")
        if hasattr(application.state, "outbox_task"):
            application.state.outbox_task.cancel()
        if hasattr(application.state, "shipment_task"):
            application.state.shipment_task.cancel()
        await application.state.http_session.close()
        if hasattr(application.state, "kafka_producer"):
            await application.state.kafka_producer.stop()
        logger.info("LIFESPAN | Application shutdown completed successfully")

    except Exception as exception:
        logger.error("Critical initialization failure detected", error=str(exception))
        raise
