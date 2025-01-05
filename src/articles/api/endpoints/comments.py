from typing import Any

from fastapi import APIRouter, Query

from src.articles.api.deps import DbSession, CurrentUser
from src.articles.schemas.base import PaginationSchema
from src.articles.schemas.comment import Comment, CommentCreate, CommentUpdate
from src.articles.services.comment import CommentService
from src.articles.utils.decorators import endpoint_decorator

comments_router = APIRouter()


@comments_router.post("", response_model=Comment)
@endpoint_decorator(
    summary="Create a new comment on an article",
    status_code=201,
    response_model=Comment,
    description="Create a new comment on an article",
)
async def create_comment(*, db: DbSession, comment_in: CommentCreate, current_user: CurrentUser) -> Any:
    comment_service = CommentService(db)
    comment_in = CommentCreate(
        content=comment_in.content,
        article_id=comment_in.article_id,
        user_id=current_user.id
    )
    comment = await comment_service.create(obj=comment_in)
    return comment


@comments_router.get("/{comment_id}", response_model=Comment)
@endpoint_decorator(summary="Get a comment on an article", response_model=Comment)
async def get_comment(*, db: DbSession, comment_id: int) -> Any:
    comment_service = CommentService(db)
    return await comment_service.get_by_id(comment_id)


@comments_router.put("/{comment_id}", response_model=Comment)
@endpoint_decorator(summary="Update a comment on an article", response_model=Comment)
async def update_comment(*, db: DbSession, comment_id: int, comment_in: CommentUpdate, current_user: CurrentUser) -> Any:
    comment_service = CommentService(db)
    return await comment_service.update(obj_id=comment_id, obj=comment_in, user_id=current_user.id)


@comments_router.delete("/{comment_id}", response_model=Comment)
@endpoint_decorator(summary="Delete a comment on an article", response_model=Comment)
async def delete_comment(*, db: DbSession, comment_id: int, current_user: CurrentUser) -> Any:
    comment_service = CommentService(db)
    return await comment_service.delete(obj_id=comment_id, user_id=current_user.id)


@comments_router.get("/article/{article_id}", response_model=PaginationSchema[Comment])
@endpoint_decorator(summary="Get paginated comments for an article", response_model=PaginationSchema[Comment])
async def get_article_comments(
    *,
    db: DbSession,
    article_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> Any:
    comment_service = CommentService(db)
    return await comment_service.get_paginated_by_article(
        article_id=article_id,
        page=page,
        page_size=page_size
    )

