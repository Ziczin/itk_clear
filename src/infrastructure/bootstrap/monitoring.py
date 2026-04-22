import sentry_sdk

from src.config import settings
from src.utils.logger import logger


async def initialize_sentry_monitoring():
    """Configure Sentry SDK for error tracking if DSN is provided."""
    logger.info("SENTRY BOOTSTRAP | Initializing Sentry monitoring")
    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)
        logger.info("SENTRY BOOTSTRAP | Sentry monitoring integration enabled")
    else:
        logger.info("SENTRY BOOTSTRAP | Sentry DSN not provided, monitoring disabled")
