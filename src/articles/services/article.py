from typing import List

from fastapi import HTTPException
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.article import Article
from src.articles.repositories.article import ArticleRepository
from src.articles.repositories.author import AuthorRepository
from src.articles.repositories.base import BaseRepository
from src.articles.repositories.tag import TagRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate
from src.articles.services.base import BaseService, ModelType


class ArticleService(BaseService[Article, ArticleCreate, ArticleUpdate, ArticleRepository]):
    owner_field = "owner_id"

    def __init__(self, db: AsyncSession):
        super().__init__(ArticleRepository, db)
        self.author_repository = AuthorRepository(db)
        self.tag_repository = TagRepository(db)

    async def create(self, *, obj: ArticleCreate) -> Article:
        authors = await self._get_authors_by_ids(obj.author_ids)
        tags = await self._get_tags_by_ids(obj.tag_ids)

        article_data = obj.model_dump(exclude={"author_ids", "tag_ids"})
        return await self.repository.create_with_relationships(
            obj_in_data=article_data,
            authors=authors,
            tags=tags,
        )

    async def update(self, *, obj_id: int, obj: ArticleUpdate, user_id: int) -> Article:
        article = await self.repository.get_by_id(obj_id)
        if not article:
            raise HTTPException(status_code=404, detail=f"Article {obj_id} not found")

        await self._check_ownership(db_obj=article, user_id=user_id)

        if not article:
            raise HTTPException(status_code=404, detail=f"Article {obj_id} not found")

        if obj.author_ids is not None:
            article.authors = await self._get_authors_by_ids(obj.author_ids)

        if obj.tag_ids is not None:
            article.tags = await self._get_tags_by_ids(obj.tag_ids)

        updated_data = obj.model_dump(exclude={"author_ids", "tag_ids"}, exclude_unset=True)

        return await self.repository.update(db_obj=article, obj_in=updated_data)

    async def _get_entities_by_ids(self, *, ids: Sequence[int], base_repository: BaseRepository, entity_name: str) -> List[ModelType]:
        """Helper method to fetch multiple entities by ids and validate that they exist"""
        entities = []
        for entity_id in ids:
            entity = await base_repository.get_by_id(entity_id)
            if not entity:
                raise HTTPException(status_code=404, detail=f"{entity_name} {entity_id} not found")
            entities.append(entity)
        return entities

    async def _get_authors_by_ids(self, author_ids: Sequence[int]) -> List[ModelType]:
        """Helper method to fetch authors by their ids"""
        return await self._get_entities_by_ids(ids=author_ids, base_repository=self.author_repository, entity_name="Author")

    async def _get_tags_by_ids(self, tag_ids: Sequence[int]) -> List[ModelType]:
        """Helper method to fetch tags by their ids"""
        return await self._get_entities_by_ids(ids=tag_ids, base_repository=self.tag_repository, entity_name="Tag")

