from typing import Optional

from pydantic import BaseModel

from src.articles.schemas.base import BaseSchema


class TagBase(BaseSchema):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None


class Tag(TagBase):
    id: int


