import asyncio
import aiohttp
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.infrastructure.database import engine, Base
from src.infrastructure.messaging import (
    KafkaProducer,
    OutboxPublisher,
    ShipmentConsumer,
)
from src.infrastructure.uow import UoW
from src.infrastructure.clients.notify import NotifyClient
from src.application.usecases.shipment_event import ShipmentEventUC
from src.presentation.routes import router
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup, background workers, and shutdown sequence."""
    async with logger("App.Lifespan"):
        logger.info("Initializing application components")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema synchronized")
            app.state.http_session = aiohttp.ClientSession()
            logger.info("HTTP client session established")
            app.state.broker = KafkaProducer()
            await app.state.broker.start()
            logger.info("Kafka producer connected")
            pub_task = asyncio.create_task(OutboxPublisher(UoW, app.state.broker).run())
            logger.info("Outbox publisher worker started")
            cancel_evt = asyncio.Event()

            def uc_factory():
                return ShipmentEventUC(UoW(), NotifyClient(app.state.http_session))

            cons_task = asyncio.create_task(
                ShipmentConsumer(uc_factory, app.state.http_session).run(cancel_evt)
            )
            logger.info("Shipment consumer worker started")
            yield
            logger.info("Initiating graceful shutdown sequence")
            pub_task.cancel()
            cons_task.cancel()
            await app.state.http_session.close()
            await app.state.broker.stop()
            logger.info("Application shutdown completed successfully")
        except Exception as e:
            logger.error("Critical initialization failure detected", error=str(e))
            raise


app = FastAPI(lifespan=lifespan, title="Capashino Order Service")
app.include_router(router)
