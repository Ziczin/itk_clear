from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
import asyncio
from src.core.config import settings
from src.utils.logger import logger


class KafkaProducer:
    """Wrapper around aiokafka for event publishing."""

    def __init__(self):
        self.producer = None

    async def start(self):
        """Establish connection to Kafka broker cluster."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await self.producer.start()

    async def stop(self):
        """Gracefully close Kafka producer connection."""
        if self.producer:
            await self.producer.stop()

    async def publish(self, topic: str, key: str, val: dict):
        """Send event payload to specified topic with ordering key."""
        await self.producer.send_and_wait(
            topic, key=key.encode(), value=json.dumps(val).encode()
        )


class OutboxPublisher:
    """Background worker polling outbox and publishing to Kafka."""

    def __init__(self, uow_factory, broker: KafkaProducer, interval=5):
        self.uow_factory = uow_factory
        self.broker = broker
        self.interval = interval

    async def run(self):
        """Continuously process pending outbox events."""
        async with logger("Worker.OutboxPublisher"):
            while True:
                try:
                    async with self.uow_factory() as uow:
                        pending = await uow.outbox.get_pending()
                        if not pending:
                            await asyncio.sleep(self.interval)
                            continue
                        for e in pending:
                            try:
                                await self.broker.publish(
                                    "student_system-order.events",
                                    str(e.idempotency_key),
                                    e.payload,
                                )
                                await uow.outbox.mark_published(e.id)
                                await uow.commit()

                                logger.info(
                                    "Outbox event published",
                                    event_id=str(e.id),
                                    topic="order.events",
                                )

                            except Exception as err:
                                await uow.rollback()

                                logger.error(
                                    "Publish failed, transaction rolled back",
                                    event_id=str(e.id),
                                    error=str(err),
                                )

                except Exception as err:
                    logger.error("Outbox polling loop critical failure", error=str(err))

                await asyncio.sleep(self.interval)


class ShipmentConsumer:
    """Background worker consuming shipping events from Kafka."""

    def __init__(self, uc_factory, http_session):
        self.uc_factory = uc_factory
        self.session = http_session

    async def run(self, cancel_event: asyncio.Event):
        """Continuously read shipment messages and delegate to use case."""
        async with logger("Worker.ShipmentConsumer"):
            consumer = AIOKafkaConsumer(
                "student_system-shipment.events",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="order-svc-group",
            )
            await consumer.start()
            try:
                async for msg in consumer:
                    try:
                        data = json.loads(msg.value)
                        uc = self.uc_factory()
                        await uc.execute(data)
                        await consumer.commit()

                        logger.info(
                            "Shipment message processed and committed",
                            partition=msg.partition,
                            offset=msg.offset,
                        )

                    except Exception as err:
                        logger.error(
                            "Message processing failed, committing to avoid poison pill",
                            error=str(err),
                        )
                        
                        await consumer.commit()
            finally:
                await consumer.stop()
                cancel_event.set()
