import asyncio

from alembic.config import Config

from alembic import command
from src.config import settings
from src.utils.logger import logger


async def apply_migrations():
    """Apply Alembic migrations using sync command in async context."""
    logger.info("ALEMBIC BOOTSTRAP | Applying database migrations")
    alembic_cfg = Config("alembic.ini")
    # Используем синхронную версию URL для Alembic
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

    def _run_migrations():
        command.upgrade(alembic_cfg, "head")

    await asyncio.to_thread(_run_migrations)
    logger.info("ALEMBIC BOOTSTRAP | Database migrations applied successfully")
