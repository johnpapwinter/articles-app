from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.user import User
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.user import UserCreate, UserUpdate
from src.articles.utils.decorators import log_database_operations


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    @log_database_operations
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        get a user by username
        :param username: the username string
        :return: the user found in the database or None if the user does not exist
        """
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @log_database_operations
    async def create_user(self, *, obj_in: UserCreate) -> User:
        """Special create method for users to handle transaction properly"""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.flush()

        query = select(self.model).where(self.model.id == db_obj.id)
        result = await self.db.execute(query)
        return result.scalar_one()

