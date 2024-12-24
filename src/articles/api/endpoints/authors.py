from typing import Any

from fastapi import APIRouter

from src.articles.api.deps import DbSession
from src.articles.schemas.author import Author, AuthorCreate
from src.articles.services.author import AuthorService

author_router = APIRouter()


@author_router.post('', response_model=Author)
async def create_author(*, db: DbSession, author_in: AuthorCreate) -> Any:
    author_service = AuthorService(db)
    author = await author_service.create(obj=author_in)
    return author





