from typing import Optional

from pydantic import BaseModel

from src.articles.schemas.base import BaseSchema


class CommentBase(BaseSchema):
    content: str
    article_id: int
    user_id: int


class CommentCreate(CommentBase):
    article_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: int
