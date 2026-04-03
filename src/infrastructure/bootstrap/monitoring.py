import sentry_sdk
from src.config import settings
from src.utils.logger import logger


async def initialize_sentry_monitoring():
    """Configure Sentry SDK for error tracking if DSN is provided."""
    async with logger("Bootstrap.Monitoring"):
        if settings.SENTRY_DSN:
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)
            logger.info("Sentry monitoring integration enabled")
        else:
            logger.info("Sentry DSN not provided, monitoring disabled")
