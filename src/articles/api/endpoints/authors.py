from typing import Any

from fastapi import APIRouter

from src.articles.api.deps import DbSession
from src.articles.schemas.author import Author, AuthorCreate
from src.articles.services.author import AuthorService
from src.articles.utils.decorators import endpoint_decorator

author_router = APIRouter()


@author_router.post('', response_model=Author)
@endpoint_decorator(
    summary="Create a new author",
    status_code=201,
    response_model=Author,
    description='Create a new author',
)
async def create_author(*, db: DbSession, author_in: AuthorCreate) -> Any:
    author_service = AuthorService(db)
    author = await author_service.create(obj=author_in)
    return author





