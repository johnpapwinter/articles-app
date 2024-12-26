from math import ceil
from typing import List

from fastapi import HTTPException
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.core.error_messages import ErrorMessages
from src.articles.models.article import Article
from src.articles.repositories.article import ArticleRepository
from src.articles.repositories.author import AuthorRepository
from src.articles.repositories.base import BaseRepository
from src.articles.repositories.tag import TagRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate, ArticleSearchFilters, ArticleSchema
from src.articles.schemas.base import PaginationSchema
from src.articles.services.base import BaseService, ModelType


class ArticleService(BaseService[Article, ArticleCreate, ArticleUpdate, ArticleRepository]):
    owner_field = "owner_id"

    def __init__(self, db: AsyncSession):
        super().__init__(ArticleRepository, db)
        self.author_repository = AuthorRepository(db)
        self.tag_repository = TagRepository(db)

    async def create(self, *, obj: ArticleCreate) -> Article:
        async with self.db.begin_nested():
            authors = await self._get_authors_by_ids(obj.author_ids)
            tags = await self._get_tags_by_ids(obj.tag_ids)

            article_data = obj.model_dump(exclude={"author_ids", "tag_ids"})
            return await self.repository.create_with_relationships(
                obj_in_data=article_data,
                authors=authors,
                tags=tags,
            )

    async def update(self, *, obj_id: int, obj: ArticleUpdate, user_id: int) -> Article:
        async with self.db.begin_nested():
            article = await self.repository.get_by_id(obj_id)
            if not article:
                raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND.value)

            await self._check_ownership(db_obj=article, user_id=user_id)

            if obj.author_ids is not None:
                article.authors = await self._get_authors_by_ids(obj.author_ids)

            if obj.tag_ids is not None:
                article.tags = await self._get_tags_by_ids(obj.tag_ids)

            updated_data = obj.model_dump(exclude={"author_ids", "tag_ids"}, exclude_unset=True)

            return await self.repository.update(db_obj=article, obj_in=updated_data)

    async def search(self, *, search_params: ArticleSearchFilters, page: int = 1, page_size: int = 10) -> PaginationSchema[ArticleSchema]:
        items, total_items = await self.repository.search_with_filters(
            search_params=search_params,
            page=page,
            page_size=page_size
        )

        total_pages = ceil(total_items / page_size)
        return PaginationSchema(
            items=items,
            current_page=page,
            total_pages=total_pages,
            total_items=total_items,
        )

    async def _get_entities_by_ids(self, *, ids: Sequence[int], base_repository: BaseRepository) -> List[ModelType]:
        """Helper method to fetch multiple entities by ids and validate that they exist"""
        entities = []
        for entity_id in ids:
            entity = await base_repository.get_by_id(entity_id)
            if not entity:
                raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND.value)
            entities.append(entity)
        return entities

    async def _get_authors_by_ids(self, author_ids: Sequence[int]) -> List[ModelType]:
        """Helper method to fetch authors by their ids"""
        return await self._get_entities_by_ids(ids=author_ids, base_repository=self.author_repository)

    async def _get_tags_by_ids(self, tag_ids: Sequence[int]) -> List[ModelType]:
        """Helper method to fetch tags by their ids"""
        return await self._get_entities_by_ids(ids=tag_ids, base_repository=self.tag_repository)

