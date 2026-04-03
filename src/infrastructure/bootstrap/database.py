from alembic.config import Config
from alembic import command
from src.config import settings
from src.utils.logger import logger


async def apply_migrations():
    """Run Alembic migrations to synchronize database schema."""
    async with logger("Bootstrap.Database"):
        alembic_config = Config("alembic.ini")
        alembic_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(alembic_config, "head")
        logger.info("Database migrations applied successfully")
