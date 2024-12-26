from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.tag import Tag
from src.articles.repositories.tag import TagRepository
from src.articles.schemas.tag import TagCreate, TagUpdate
from src.articles.services.base import BaseService


class TagService(BaseService[Tag, TagCreate, TagUpdate, TagRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(TagRepository, db)

    async def create(self, *, obj: TagCreate) -> Tag:
        async with self.db.begin_nested():
            existing_tag = await self.repository.get_by_name(obj.name)
            if existing_tag:
                return existing_tag
            return await super().create(obj=obj)

