import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config import settings
from src.utils.logger import logger, set_request_id


class KafkaProducerWrapper:
    """Wrapper around aiokafka for reliable event publishing."""

    def __init__(self):
        self.producer = None

    async def start(self):
        """Establish connection to the Kafka broker cluster."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await self.producer.start()

    async def stop(self):
        """Gracefully terminate the Kafka producer connection."""
        if self.producer:
            await self.producer.stop()

    async def publish(self, topic: str, key: str, value: dict):
        """Send an event payload to a specified topic with an ordering key."""
        await self.producer.send_and_wait(
            topic, key=key.encode(), value=json.dumps(value).encode()
        )


class OutboxPublisher:
    """Background worker polling outbox and publishing to Kafka."""

    def __init__(self, uow_factory, broker: KafkaProducerWrapper, interval=5):
        self.uow_factory = uow_factory
        self.broker = broker
        self.interval = interval

    async def run(self):
        """Continuously process pending outbox events."""
        logger.info("Worker.OutboxPublisher started")
        set_request_id()
        while True:
            try:
                async with self.uow_factory() as uow:
                    pending_events = await uow.outbox.get_pending()
                    if not pending_events:
                        await asyncio.sleep(self.interval)

                        continue

                    for event in pending_events:
                        try:
                            await self.broker.publish(
                                topic="student_system-order.events",
                                key=str(event.idempotency_key),
                                value=event.payload,
                            )
                            await uow.outbox.mark_as_published(entry_id=event.id)
                            await uow.commit()
                            logger.info(
                                "Outbox event published",
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

    def __init__(self, uc_factory, http_session):
        self.uc_factory = uc_factory
        self.session = http_session

    async def run(self, cancel_event: asyncio.Event):
        """Continuously read shipment messages and delegate to use case."""
        logger.info("Worker.ShipmentConsumer started")
        consumer = AIOKafkaConsumer(
            "student_system-shipment.events",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="order-svc-group",
        )
        await consumer.start()

        try:
            async for message in consumer:
                try:
                    event_data = json.loads(message.value)
                    use_case = self.uc_factory()
                    await use_case.execute(event_data=event_data)
                    logger.info(
                        "Shipment message processed",
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
