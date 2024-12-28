from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.auth.password_utils import get_password_hash, verify_password
from src.articles.core.error_messages import ErrorMessages
from src.articles.models.user import User
from src.articles.repositories.user import UserRepository
from src.articles.schemas.user import UserCreate, UserUpdate
from src.articles.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository, db)

    async def create(self, *, obj: UserCreate) -> User:
        """
        create a new user
        :param obj: the user to be created
        :return: the created user
        """
        async with self.db.begin_nested():
            existing_user = await self.repository.get_by_username(username=obj.username)
            if existing_user:
                raise HTTPException(status_code=400, detail=ErrorMessages.USERNAME_ALREADY_EXISTS.value)

            hashed_password = get_password_hash(obj.password)
            user_data = UserCreate(username=obj.username, password=hashed_password)

            return await self.repository.create_user(obj_in=user_data)

    async def authenticate(self, *, username: str, password: str) -> User | None:
        """Authenticate a user by username and password."""
        user = await self.repository.get_by_username(username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


