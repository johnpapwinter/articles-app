from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.auth.password_utils import get_password_hash, verify_password
from src.articles.models.user import User
from src.articles.repositories.user import UserRepository
from src.articles.schemas.user import UserCreate, UserUpdate
from src.articles.services.base import BaseService, CreateSchemaType, ModelType


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository, db)

    async def create(self, *, obj: UserCreate) -> User:
        existing_user = await self.repository.get_by_username(username=obj.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

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


