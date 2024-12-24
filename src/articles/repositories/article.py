from typing import List, Optional, Union, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.articles.models.article import Article
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate


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
        async with self.transaction():
            db_obj = self.model(**obj_in_data)

            db_obj.authors = authors
            db_obj.tags = tags

            self.db.add(db_obj)
            await self.db.commit()

            query = select(self.model).options(
                selectinload(self.model.authors),
                selectinload(self.model.tags),
            ).where(self.model.id == db_obj.id)

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

    async def update(self, *, db_obj: Article, obj_in: Union[ArticleUpdate, Dict[str, Any]]) -> Article:
        async with self.transaction():
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)


            for field in update_data:
                if field not in ["authors", "tags"] and hasattr(db_obj, field):
                    setattr(self, field, update_data[field])

            await self.db.flush()

            query = select(self.model).options(
                selectinload(self.model.authors),
                selectinload(self.model.tags),
            ).where(self.model.id == db_obj.id)

            result = await self.db.execute(query)
            return result.scalar_one_or_none()




