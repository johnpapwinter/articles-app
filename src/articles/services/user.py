from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.user import User
from src.articles.repositories.user import UserRepository
from src.articles.schemas.user import UserCreate, UserUpdate
from src.articles.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository, db)





