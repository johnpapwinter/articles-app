from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.articles.schemas.author import AuthorCreate, Author
from src.articles.schemas.base import BaseSchema
from src.articles.schemas.tag import TagCreate, Tag


class ArticleBase(BaseSchema):
    title: str
    abstract: str
    publication_date: datetime


class ArticleCreate(ArticleBase):
    author_ids: List[int]
    tag_ids: List[int]
    owner_id: Optional[int] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    author_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class Article(ArticleBase):
    id: int
    authors: List[Author]
    tags: List[Tag]
    owner_id: int


class ArticleSearchFilters(BaseModel):
    title: Optional[str] = None
    publication_year: Optional[int] = None
    author: Optional[str] = None
