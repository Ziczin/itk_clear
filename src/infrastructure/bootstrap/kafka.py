from src.infrastructure.messaging import KafkaProducerWrapper
from src.utils.logger import logger


async def initialize_kafka_producer():
    """Start Kafka producer and store instance in application state."""
    async with logger("Bootstrap.Kafka"):
        producer = KafkaProducerWrapper()
        await producer.start()
        logger.info("Kafka producer connected and ready")
        return producer
