from typing import Any

from fastapi import APIRouter, Query

from src.articles.api.deps import DbSession, CurrentUser
from src.articles.core.dependencies import get_elasticsearch_client
from src.articles.repositories.search_repository import ArticleSearchRepository
from src.articles.schemas.article import ArticleSchema, ArticleCreate, ArticleUpdate, ArticleSearchFilters
from src.articles.schemas.base import PaginationSchema
from src.articles.services.article import ArticleService

article_router = APIRouter()


@article_router.post("/create", response_model=ArticleSchema)
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
async def get_article(*, db: DbSession, article_id: int) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.get_by_id(article_id)


@article_router.put("/{article_id}", response_model=ArticleSchema)
async def update_article(*, db: DbSession, article_id: int, article: ArticleUpdate, current_user: CurrentUser) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.update(obj_id=article_id, obj=article, user_id=current_user.id)


@article_router.delete("/{article_id}", response_model=ArticleSchema)
async def delete_article(*, db: DbSession, article_id: int, current_user: CurrentUser) -> Any:
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    return await article_service.delete(obj_id=article_id, user_id=current_user.id)


@article_router.post("/search", response_model=PaginationSchema[ArticleSchema])
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


@article_router.get("/elastic")
async def test_search(*, db: DbSession, query: str = Query(..., min_length=1)):
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    article_service = ArticleService(db, search_repository)
    await article_service.test_search(query=query, fuzzy=True)


@article_router.get("/search/status")
async def check_search_status() -> dict:
    """
    Returns the current status of the search index, including:
    - Number of indexed documents
    - Index settings
    - Index health status
    """
    search_repository = ArticleSearchRepository(get_elasticsearch_client())
    return await search_repository.verify_index_status()


@article_router.get("/search/test")
async def test_search(
        *,
        query: str,  # The text we want to search for
) -> dict:
    """
    Tests Elasticsearch search functionality by performing a search and returning detailed results.
    This endpoint helps verify:
    1. If Elasticsearch is properly indexing abstracts
    2. How well the search matches work
    3. What articles are being found and their relevance scores
    """
    # Create our repositories
    search_repository = ArticleSearchRepository(get_elasticsearch_client())

    try:
        # Perform the search with detailed results
        search_result = await search_repository.test_search_functionality(query)
        return search_result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "details": "Failed to perform search test"
        }
