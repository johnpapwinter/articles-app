from typing import Any

from fastapi import APIRouter, Depends

from src.articles.api.deps import DbSession
from src.articles.auth.deps import get_current_user
from src.articles.models import User
from src.articles.schemas.comment import Comment, CommentCreate, CommentUpdate
from src.articles.services.comment import CommentService

comments_router = APIRouter()


@comments_router.post("", response_model=Comment)
async def create_comment(
        *,
        db: DbSession,
        comment_in: CommentCreate,
        current_user: User = Depends(get_current_user)) -> Any:
    comment_service = CommentService(db)
    comment = await comment_service.create(obj=comment_in)
    return comment


@comments_router.get("/{comment_id}", response_model=Comment)
async def get_comment(*, db: DbSession, comment_id: int) -> Any:
    comment_service = CommentService(db)
    return await comment_service.get_by_id(comment_id)


@comments_router.put("/{comment_id}", response_model=Comment)
async def update_comment(
        *,
        db: DbSession,
        comment_id: int,
        comment_in: CommentUpdate,
        current_user: User = Depends(get_current_user)) -> Any:
    comment_service = CommentService(db)
    return await comment_service.update(obj_id=comment_id, obj=comment_in)


@comments_router.delete("/{comment_id}", response_model=Comment)
async def delete_comment(
        *,
        db: DbSession,
        comment_id: int,
        current_user: User = Depends(get_current_user)) -> Any:
    comment_service = CommentService(db)
    return await comment_service.delete(obj_id=comment_id)

