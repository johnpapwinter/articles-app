from typing import Optional

from pydantic import BaseModel

from src.articles.schemas.base import BaseSchema


class AuthorBase(BaseSchema):
    name: str


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = None


class Author(AuthorBase):
    id: int


