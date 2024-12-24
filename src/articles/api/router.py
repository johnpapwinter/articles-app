from fastapi import APIRouter

from src.articles.api.endpoints import articles, authors, tags, users, comments, auth

api_router = APIRouter()

api_router.include_router(articles.article_router, prefix="/articles", tags=["articles"])
api_router.include_router(authors.author_router, prefix="/authors", tags=["authors"])
api_router.include_router(tags.tags_router, prefix="/tags", tags=["tags"])
api_router.include_router(users.users_router, prefix="/users", tags=["users"])
api_router.include_router(comments.comments_router, prefix="/comments", tags=["comments"])
api_router.include_router(auth.auth_router, prefix="/auth", tags=["auth"])
