from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.db import AsyncSessionLocal
from src.articles.utils.logging import setup_logging

logger = setup_logging(__name__)


async def init_version_tables(session: AsyncSession) -> None:
    """Initialize versioning tables"""
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS versioning.transaction (
            id BIGSERIAL PRIMARY KEY,
            issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            remote_addr VARCHAR(50)
        )
    """))
    await session.commit()


async def init_db() -> None:
    """Initialize database tables using Alembic migrations"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if tables exist
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                );
            """))
            has_tables = result.scalar()

            if not has_tables:
                logger.info("No tables found. Running migrations...")
                alembic_config = Config("alembic.ini")
                command.upgrade(alembic_config, "head")
                logger.info("Database migrations completed")
            else:
                logger.info("Database tables already exist")

            await session.commit()

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            await session.rollback()
            raise

