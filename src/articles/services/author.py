from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.author import Author
from src.articles.repositories.author import AuthorRepository
from src.articles.schemas.author import AuthorCreate, AuthorUpdate
from src.articles.services.base import BaseService


class AuthorService(BaseService[Author, AuthorCreate, AuthorUpdate, AuthorRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuthorRepository, db)

    async def create(self, *, obj: AuthorCreate) -> Author:
        """
        Create a new author or if the author exists, return it.
        :param obj: the new author
        :return: the existing or created author
        """
        async with self.db.begin_nested():
            existing_author = await self.repository.get_by_name(obj.name)
            if existing_author:
                return existing_author
            return await super().create(obj=obj)

