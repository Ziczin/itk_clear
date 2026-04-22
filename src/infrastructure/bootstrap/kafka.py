from src.infrastructure.messaging import KafkaProducerWrapper
from src.utils.logger import logger


async def initialize_kafka_producer():
    """Start Kafka producer and store instance in application state."""
    logger.info("KAFKA BOOTSTRAP | Initializing Kafka producer")
    producer = KafkaProducerWrapper()
    await producer.start()
    logger.info("KAFKA BOOTSTRAP | Kafka producer connected and ready")
    return producer
