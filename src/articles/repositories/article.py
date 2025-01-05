from typing import List, Optional, Union, Dict, Any, Tuple

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.articles.models import Author
from src.articles.models.article import Article
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.article import ArticleCreate, ArticleUpdate, ArticleSearchFilters
from src.articles.utils.decorators import log_database_operations


class ArticleRepository(BaseRepository[Article, ArticleCreate, ArticleUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Article, db)

    @log_database_operations
    async def get_by_id(self, obj_id: int) -> Optional[Article]:
        """
        get an article by id from the database
        :param obj_id: the article id to get
        :return: a found article or None
        """
        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        ).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @log_database_operations
    async def create_with_relationships(
            self,
            *,
            obj_in_data: dict,
            authors: List["Author"],
            tags: List["Tag"]
    ) -> Article:
        """
        create an article with relationships with authors and tags
        :param obj_in_data: the article data to be created
        :param authors: the authors associated with the article
        :param tags: the tags associated with the article
        :return: the created article
        """
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

    @log_database_operations
    async def update(self, *, db_obj: Article, obj_in: Union[ArticleUpdate, Dict[str, Any]]) -> Article:
        """
        update an article from the database
        :param db_obj: the article as it currently is in the database
        :param obj_in: the updated article data
        :return: the updated article
        """
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

    @log_database_operations
    async def search_with_filters(
            self,
            *,
            search_params: ArticleSearchFilters,
            elastic_ids: Optional[List[int]] = None,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[Article], int]:
        """
        search the article with the given filters
        :param search_params: the filters to search for
        :param elastic_ids: the ids found in the text search in elasticsearch
        :param page: the page number of the result
        :param page_size: the size of the page of the result
        :return: a tuple of a list of found articles and the page number
        """
        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        )

        if elastic_ids is not None:
            query = query.filter(self.model.id.in_(elastic_ids))

        if search_params.title:
            query = query.filter(func.lower(self.model.title).contains(search_params.title.lower()))

        if search_params.publication_year:
            query = query.filter(extract('year', self.model.publication_date) == search_params.publication_year)

        if search_params.author:
            query = query.join(self.model.authors).filter(
                func.lower(Author.name).contains(search_params.author.lower())
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()


        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total

    @log_database_operations
    async def get_all_with_filters(
            self,
            *,
            search_params: ArticleSearchFilters,
            elastic_ids: Optional[List[int]]
    ) -> List[Article]:
        """
        get all articles based on the given filters
        :param search_params: the filters to search for
        :param elastic_ids: the elasticsearch ids found in the text search in elasticsearch
        :return: the list of articles
        """
        query = select(self.model).options(
            selectinload(self.model.authors),
            selectinload(self.model.tags),
        )

        if elastic_ids is not None:
            query = query.filter(self.model.id.in_(elastic_ids))

        if search_params.title:
            query = query.filter(func.lower(self.model.title).contains(search_params.title.lower()))

        if search_params.publication_year:
            query = query.filter(extract('year', self.model.publication_date) == search_params.publication_year)

        if search_params.author:
            query = query.join(self.model.authors).filter(
                func.lower(Author.name).contains(search_params.author.lower())
            )

        result = await self.db.execute(query)
        return result.scalars().all()

