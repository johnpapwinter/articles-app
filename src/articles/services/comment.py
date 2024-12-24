from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.comment import Comment
from src.articles.repositories.comment import CommentRepository
from src.articles.schemas.comment import CommentCreate, CommentUpdate
from src.articles.services.base import BaseService


class CommentService(BaseService[Comment, CommentCreate, CommentUpdate, CommentRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(CommentRepository, db)

