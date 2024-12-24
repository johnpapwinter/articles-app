from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.tag import Tag
from src.articles.repositories.base import BaseRepository
from src.articles.schemas.tag import TagCreate, TagUpdate


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tag, db)
