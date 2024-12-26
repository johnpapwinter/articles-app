from typing import List, Optional, Union, Dict, Any, Tuple

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.articles.models import Author
from src.articles.models.article import Article
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate, ArticleSearchFilters


class ArticleRepository(BaseRepository[Article, ArticleCreate, ArticleUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Article, db)

    async def get_by_id(self, obj_id: int) -> Optional[Article]:
        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        ).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_with_relationships(
            self,
            *,
            obj_in_data: dict,
            authors: List["Author"],
            tags: List["Tag"]
    ) -> Article:
        db_obj = self.model(**obj_in_data)

        db_obj.authors = authors
        db_obj.tags = tags

        self.db.add(db_obj)
        await self.db.flush()

        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        ).where(self.model.id == db_obj.id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, *, db_obj: Article, obj_in: Union[ArticleUpdate, Dict[str, Any]]) -> Article:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if field not in ["authors", "tags"] and hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.flush()

        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        ).where(self.model.id == db_obj.id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def search_with_filters(
            self,
            *,
            search_params: ArticleSearchFilters,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[Article], int]:
        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        )

        if search_params.title:
            query = query.filter(func.lower(self.model.title).contains(search_params.title.lower()))

        if search_params.publication_year:
            query = query.filter(extract('year', self.model.publication_date) == search_params.publication_year)

        if search_params.author:
            query = query.join(self.model.authors).filter(
                func.lower(Author.name).contains(search_params.author.lower())
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total


