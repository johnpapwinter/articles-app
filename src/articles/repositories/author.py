from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.author import Author
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.author import AuthorCreate, AuthorUpdate


class AuthorRepository(BaseRepository[Author, AuthorCreate, AuthorUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Author, db)
