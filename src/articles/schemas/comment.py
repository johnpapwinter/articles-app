from typing import Optional

from pydantic import BaseModel

from src.articles.schemas.base import BaseSchema


class CommentBase(BaseSchema):
    content: str
    article_id: int


class CommentCreate(CommentBase):
    user_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: int
    user_id: int
