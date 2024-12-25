from typing import Any

from fastapi import APIRouter

from src.articles.api.deps import DbSession, CurrentUser
from src.articles.schemas.article import Article, ArticleCreate, ArticleUpdate
from src.articles.services.article import ArticleService

article_router = APIRouter()


@article_router.post("", response_model=Article)
async def create_article(*, db: DbSession, article_in: ArticleCreate, current_user: CurrentUser) -> Any:
    article_service = ArticleService(db)
    article_in = ArticleCreate(
        title=article_in.title,
        abstract=article_in.abstract,
        publication_date=article_in.publication_date,
        author_ids=article_in.author_ids,
        tag_ids=article_in.tag_ids,
        owner_id=current_user.id,
    )
    article = await article_service.create(obj=article_in)
    return article


@article_router.get("/{article_id}", response_model=Article)
async def get_article(*, db: DbSession, article_id: int) -> Any:
    article_service = ArticleService(db)
    return await article_service.get_by_id(article_id)


@article_router.put("/{article_id}", response_model=Article)
async def update_article(*, db: DbSession, article_id: int, article: ArticleUpdate, current_user: CurrentUser) -> Any:
    article_service = ArticleService(db)
    return await article_service.update(obj_id=article_id, obj=article)


@article_router.delete("/{article_id}", response_model=Article)
async def delete_article(*, db: DbSession, article_id: int, current_user: CurrentUser) -> Any:
    article_service = ArticleService(db)
    return await article_service.delete(obj_id=article_id)

