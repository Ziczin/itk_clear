import asyncio
from src.infrastructure.messaging import OutboxPublisher, ShipmentConsumer
from src.infrastructure.uow import UoW
from src.infrastructure.clients.notify import NotifyClient
from src.application.usecases.shipment_event import ShipmentEventUseCase
from src.utils.context_vars import logger


def _build_shipment_use_case_factory(http_session):
    """Create a factory function for instantiating shipment event use cases."""

    def factory():
        return ShipmentEventUseCase(
            uow=UoW(), notification_client=NotifyClient(session=http_session)
        )

    return factory


async def start_background_workers(application, http_session):
    """Launch outbox publisher and shipment consumer as background tasks."""
    logger.info("Starting background workers")
    outbox_publisher = OutboxPublisher(
        uow_factory=UoW, broker=application.state.kafka_producer
    )
    application.state.outbox_task = asyncio.create_task(outbox_publisher.run())
    logger.info("Outbox publisher worker started")

    shutdown_event = asyncio.Event()
    consumer_task = asyncio.create_task(
        ShipmentConsumer(
            uc_factory=_build_shipment_use_case_factory(http_session),
            http_session=http_session,
        ).run(shutdown_event)
    )
    application.state.shipment_task = consumer_task
    logger.info("Shipment consumer worker started")
