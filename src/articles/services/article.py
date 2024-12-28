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
from src.articles.repositories.search_repository import ArticleSearchRepository
from src.articles.repositories.tag import TagRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate, ArticleSearchFilters, ArticleSchema
from src.articles.schemas.base import PaginationSchema
from src.articles.services.base import BaseService, ModelType


class ArticleService(BaseService[Article, ArticleCreate, ArticleUpdate, ArticleRepository]):
    owner_field = "owner_id"

    def __init__(self, db: AsyncSession, search_repository: ArticleSearchRepository):
        super().__init__(ArticleRepository, db)
        self.search_repository = search_repository
        self.author_repository = AuthorRepository(db)
        self.tag_repository = TagRepository(db)

    async def create(self, *, obj: ArticleCreate) -> Article:
        """
        create a new article
        :param obj: the article to be created
        :return: the created article
        """
        async with self.db.begin_nested():
            authors = await self._get_authors_by_ids(obj.author_ids)
            tags = await self._get_tags_by_ids(obj.tag_ids)

            article_data = obj.model_dump(exclude={"author_ids", "tag_ids"})
            article = await self.repository.create_with_relationships(
                obj_in_data=article_data,
                authors=authors,
                tags=tags,
            )
            await self.search_repository.index_article(article)
            indexed_doc = await self.search_repository.verify_article_indexed(article.id)
            if indexed_doc:
                print(f"Article {article.id} indexed")
            else:
                print(f"Article {article.id} not indexed")

            return article


    async def update(self, *, obj_id: int, obj: ArticleUpdate, user_id: int) -> Article:
        """
        update an article
        :param obj_id: the article id
        :param obj: the payload containing the updated data
        :param user_id: the user attempting to update the article
        :return: the updated article
        """
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
        """
        Dynamic search based on parameters against the articles stored in the database.
        :param search_params: pydantic object containing the parameters to search for.
        :param page: the page number
        :param page_size: the items per page
        :return: a paginated result of items
        """
        elastic_ids = None
        if search_params.abstract_search:
            elastic_ids = await self.search_repository.search_articles(
                query=search_params.abstract_search,
                fuzzy=True,
                size=1000
            )


        items, total_items = await self.repository.search_with_filters(
            search_params=search_params,
            elastic_ids=elastic_ids,
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


