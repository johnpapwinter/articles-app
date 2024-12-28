from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.db import AsyncSessionLocal
from src.articles.utils.logging import setup_logging

logger = setup_logging(__name__)

async def init_db() -> None:
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("""
                SELECT EXISTS(
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                );
            """))
            has_tables = result.scalar()

            if not has_tables:
                logger.info("No tables found. Running migrations")
                alembic_configure = Config("alembic.ini")
                command.upgrade(alembic_configure, "head")
                logger.info("Database migrations completed")
            else:
                logger.info("Database tables already exist")

        except Exception as e:
            logger.error(f"Error initializing database {e}")
            raise

