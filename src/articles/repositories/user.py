from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.user import User
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)



