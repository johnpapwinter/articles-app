from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.user import User
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, *, obj_in: UserCreate) -> User:
        """Special create method for users to handle transaction properly"""
        async with self.db.begin():
            db_obj = self.model(**obj_in.model_dump())
            self.db.add(db_obj)
            await self.db.flush()

            query = select(self.model).where(self.model.id == db_obj.id)
            result = await self.db.execute(query)
            return result.scalar_one()

