from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.comment import Comment
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __int__(self, db: AsyncSession):
        super().__init__(Comment, db)



