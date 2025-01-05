from typing import Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.comment import Comment
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)

    async def get_paginated_by_article(
            self,
            *,
            article_id: int,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[Comment], int]:
        """Get paginated comments by article."""
        offset = (page - 1) * page_size

        query = (
            select(self.model)
            .where(self.model.article_id == article_id)
            .order_by(self.model.id.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        comments = result.scalars().all()

        count_query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.article_id == article_id)
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        return comments, total



