from fastapi import APIRouter

from src.articles.api.endpoints import articles, authors, tags

api_router = APIRouter()

api_router.include_router(articles.article_router, prefix="/articles", tags=["articles"])
api_router.include_router(authors.author_router, prefix="/authors", tags=["authors"])
api_router.include_router(tags.tags_router, prefix="/tags", tags=["tags"])

