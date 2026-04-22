# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import asyncio
import json
from typing import Any, Awaitable, Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.application.ports.uow import IUoW
from src.config import settings
from src.utils.logger import logger, set_request_id


class KafkaProducerWrapper:
    """Wrapper around aiokafka for reliable event publishing."""

    def __init__(self) -> None:
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Establish connection to the Kafka broker cluster."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await self.producer.start()

    async def stop(self) -> None:
        """Gracefully terminate the Kafka producer connection."""
        if self.producer:
            await self.producer.stop()

    async def publish(self, topic: str, key: str, value: dict[str, Any]) -> None:
        """Send an event payload to a specified topic with an ordering key."""
        if self.producer is None:
            raise RuntimeError("Producer not started")

        await self.producer.send_and_wait(
            topic, key=key.encode(), value=json.dumps(value).encode()
        )


class OutboxPublisher:
    """Background worker polling outbox and publishing to Kafka."""

    def __init__(
        self,
        uow_factory: Callable[[], Awaitable[IUoW]],
        broker: KafkaProducerWrapper,
        interval: int = 5,
    ):
        self.uow_factory = uow_factory
        self.broker = broker
        self.interval = interval

    async def run(self) -> None:
        """Continuously process pending outbox events."""
        logger.info("MESSAGING | OutboxPublisher started")
        set_request_id()
        while True:
            try:
                async with await self.uow_factory() as uow:
                    pending_events = await uow.outbox.get_pending()
                    if not pending_events:
                        await asyncio.sleep(self.interval)
                        continue

                    for event in pending_events:
                        try:
                            if event.payload:
                                await self.broker.publish(
                                    topic="student_system-order.events",
                                    key=str(event.idempotency_key),
                                    value=event.payload,
                                )
                                await uow.outbox.mark_as_published(entry_id=event.id)
                                await uow.commit()
                                logger.info(
                                    "MESSAGING | Outbox event published",
                                    event_id=str(event.id),
                                    topic="order.events",
                                )
                        except Exception as error:
                            await uow.rollback()
                            logger.error(
                                "Publish failed, transaction rolled back",
                                event_id=str(event.id),
                                error=str(error),
                            )

            except Exception as error:
                logger.error("Outbox polling loop critical failure", error=str(error))

            await asyncio.sleep(self.interval)


class ShipmentConsumer:
    """Background worker consuming shipping events from Kafka."""

    def __init__(
        self,
        uc_factory: Callable[[], Any],
        http_session: Any,
    ):
        self.uc_factory = uc_factory
        self.session = http_session

    async def run(self, cancel_event: asyncio.Event) -> None:
        """Continuously read shipment messages and delegate to use case."""
        logger.info("KAFKA | ShipmentConsumer started")
        consumer = AIOKafkaConsumer(
            "student_system-shipment.events",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="order-svc-group",
        )
        await consumer.start()

        try:
            async for message in consumer:
                if message.value is None:
                    continue

                try:
                    event_data: dict[str, Any] = json.loads(message.value)
                    use_case = self.uc_factory()
                    await use_case.execute(event_data=event_data)
                    logger.info(
                        "KAFKA | Shipment message processed",
                        partition=message.partition,
                        offset=message.offset,
                    )
                except Exception as error:
                    logger.error(
                        "Message processing failed, committing to avoid poison pill",
                        error=str(error),
                    )
                finally:
                    await consumer.commit()
        finally:
            await consumer.stop()
            cancel_event.set()
