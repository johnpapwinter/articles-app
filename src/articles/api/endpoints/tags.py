from typing import Any

from fastapi import APIRouter

from src.articles.api.deps import DbSession
from src.articles.schemas.tag import Tag, TagCreate
from src.articles.services.tag import TagService

tags_router = APIRouter()


@tags_router.post("", response_model=Tag)
async def create_tag(*, db: DbSession, tag_in: TagCreate) -> Any:
    tag_service = TagService(db)
    tag = await tag_service.create(obj=tag_in)
    return tag


