import json
from aiokafka import AIOKafkaConsumer
from src.application.usecases import ProcessShipmentEventUseCase
from src.infrastructure.uow import SQLAlchemyUnitOfWork
from src.infrastructure.clients import NotificationClient
from src.utils.logger import logger
from src.core.config import settings


async def start_shipping_consumer(http_session, app_state):
    notification_client = NotificationClient(session=http_session)

    # Фабрика UseCase для каждого сообщения
    def use_case_factory():
        return ProcessShipmentEventUseCase(SQLAlchemyUnitOfWork(), notification_client)

    consumer = AIOKafkaConsumer(
        "student_system-shipment.events",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="order-service-group",
    )
    await consumer.start()

    async with logger("Kafka.Consumer.Shipping"):
        logger.info("Consumer loop started")
        try:
            async for msg in consumer:
                # Статический контекст для сообщения
                async with logger("Kafka.Consumer.ProcessMessage"):
                    msg_key = msg.key.decode() if msg.key else "no_key"
                    logger.debug(
                        "Message received", partition=msg.partition, offset=msg.offset
                    )

                    try:
                        data = json.loads(msg.value)
                        logger.info(
                            "Processing shipment event",
                            event_type=data.get("event_type"),
                            key=msg_key,
                        )

                        use_case = use_case_factory()
                        await use_case.execute(data)

                        await consumer.commit()
                        logger.info("Message committed")

                    except json.JSONDecodeError as e:
                        logger.error("Invalid JSON in Kafka message", error=str(e))
                        # Коммитим "битое" сообщение, чтобы не зацикливаться, или в DLQ
                        await consumer.commit()
                    except Exception:
                        logger.exception("Failed to process message")
                        # Не коммитим, сообщение будет перечитано
        finally:
            await consumer.stop()
            logger.warning("Consumer loop finished")
            if hasattr(app_state, "consumer_task"):
                app_state.consumer_task.cancel()
