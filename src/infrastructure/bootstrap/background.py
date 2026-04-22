import asyncio
from typing import Awaitable, Callable

from aiohttp.client import ClientSession
from fastapi import FastAPI

from src.application.ports.uow import IUoW
from src.application.usecases.shipment_event import ShipmentEventUseCase
from src.infrastructure.clients.notify import NotifyClient
from src.infrastructure.messaging import OutboxPublisher, ShipmentConsumer
from src.infrastructure.uow import UoW
from src.utils.logger import logger


def _build_uow_factory() -> Callable[[], Awaitable[IUoW]]:
    async def factory() -> IUoW:
        return UoW()

    return factory


def _build_shipment_use_case_factory(
    http_session: ClientSession,
) -> Callable[[], ShipmentEventUseCase]:
    """Create a factory function for instantiating shipment event use cases."""

    def factory() -> ShipmentEventUseCase:
        return ShipmentEventUseCase(
            uow=UoW(), notification_client=NotifyClient(session=http_session)
        )

    return factory


async def start_background_workers(application: FastAPI, http_session: ClientSession):
    """Launch outbox publisher and shipment consumer as background tasks."""
    logger.info("WORKER BOOTSTRAP | Starting background workers")
    outbox_publisher = OutboxPublisher(
        uow_factory=_build_uow_factory(), broker=application.state.kafka_producer
    )
    application.state.outbox_task = asyncio.create_task(outbox_publisher.run())
    logger.info("WORKER BOOTSTRAP | Outbox publisher worker started")

    shutdown_event = asyncio.Event()
    consumer_task = asyncio.create_task(
        ShipmentConsumer(
            uc_factory=_build_shipment_use_case_factory(http_session),
            http_session=http_session,
        ).run(shutdown_event)
    )
    application.state.shipment_task = consumer_task
    logger.info("WORKER BOOTSTRAP | Shipment consumer worker started")
