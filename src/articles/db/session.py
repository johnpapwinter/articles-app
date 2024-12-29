import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.articles.core.config.factory import get_settings

# from sqlalchemy_continuum import versioning_manager

# from src.articles.core.config import settings


settings = get_settings(os.getenv("ENVIRONMENT", "development"))


engine = create_async_engine(
    settings.POSTGRES_URI,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        await session.begin()
        try:
            # versioning_manager.uow.current_transaction = None
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()



