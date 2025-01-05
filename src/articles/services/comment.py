from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.comment import Comment
from src.articles.repositories.comment import CommentRepository
from src.articles.schemas.base import PaginationSchema
from src.articles.schemas.comment import Comment as CommentSchema
from src.articles.schemas.comment import CommentCreate, CommentUpdate
from src.articles.services.base import BaseService


class CommentService(BaseService[Comment, CommentCreate, CommentUpdate, CommentRepository]):
    owner_field = "user_id"

    def __init__(self, db: AsyncSession):
        super().__init__(CommentRepository, db)

    async def get_paginated_by_article(
            self,
            *,
            article_id: int,
            page: int = 1,
            page_size: int = 10
    ) -> PaginationSchema[CommentSchema]:
        """
        get all comments by article id paginated
        :param article_id: the article id
        :param page: the page number
        :param page_size: the size of the page
        :return: the pagination schema with the comments
        """
        comments, total_count = await self.repository.get_paginated_by_article(
            article_id=article_id, page=page, page_size=page_size
        )

        total_pages = (total_count + page_size - 1) // page_size

        return PaginationSchema(
            items=comments,
            current_page=page,
            total_pages=total_pages,
            total_items=total_count
        )
