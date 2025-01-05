import pandas as pd

from typing import Any

from fastapi import APIRouter, Query
from starlette.responses import StreamingResponse

from src.articles.api.deps import DbSession, CurrentUser
from src.articles.core.dependencies import get_elasticsearch_client
from src.articles.repositories.search_repository import ArticleSearchRepository
from src.articles.schemas.article import ArticleSchema, ArticleCreate, ArticleUpdate, ArticleSearchFilters
from src.articles.schemas.base import PaginationSchema
from src.articles.services.article import ArticleService
from src.articles.utils.decorators import endpoint_decorator

article_router = APIRouter()


@article_router.post("/create", response_model=ArticleSchema)
@endpoint_decorator(
    summary="Create a new article",
    response_model=ArticleSchema,
    status_code=201,
    description="Create a new article"
)
async def create_article(*, db: DbSession, article: ArticleCreate, current_user: CurrentUser) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    article_in = ArticleCreate(
        title=article.title,
        abstract=article.abstract,
        publication_date=article.publication_date,
        author_ids=article.author_ids,
        tag_ids=article.tag_ids,
        owner_id=current_user.id,
    )
    article = await article_service.create(obj=article_in)
    return article


@article_router.get("/get/{article_id}", response_model=ArticleSchema)
@endpoint_decorator(summary="Get an article by ID", response_model=ArticleSchema)
async def get_article(*, db: DbSession, article_id: int) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.get_by_id(article_id)


@article_router.put("/{article_id}", response_model=ArticleSchema)
@endpoint_decorator(summary="Update an article", response_model=ArticleSchema)
async def update_article(*, db: DbSession, article_id: int, article: ArticleUpdate, current_user: CurrentUser) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.update(obj_id=article_id, obj=article, user_id=current_user.id)


@article_router.delete("/{article_id}", response_model=ArticleSchema)
@endpoint_decorator(summary="Delete an article", response_model=ArticleSchema)
async def delete_article(*, db: DbSession, article_id: int, current_user: CurrentUser) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.delete(obj_id=article_id, user_id=current_user.id)


@article_router.post("/search", response_model=PaginationSchema[ArticleSchema])
@endpoint_decorator(
    summary="Search articles",
    response_model=PaginationSchema[ArticleSchema],
    description="Search articles with filters and return a paginated response."
)
async def search_articles(
        *,
        db: DbSession,
        search_params: ArticleSearchFilters,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Page size"),
) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.search(
        search_params=search_params,
        page=page,
        page_size=page_size,
    )

@article_router.post("/export-csv")
@endpoint_decorator(
    summary="Export search results as CSV",
    description="Export all articles matching the search criteria as a CSV file"
)
async def export_articles_csv(
        *,
        db: DbSession,
        search_params: ArticleSearchFilters,
) -> StreamingResponse:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)

    csv_file = await article_service.export_search_to_csv(search_params=search_params)

    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=articles_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )

