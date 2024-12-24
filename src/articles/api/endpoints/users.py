from typing import Any

from fastapi import APIRouter

from src.articles.api.deps import DbSession
from src.articles.schemas.user import User, UserCreate
from src.articles.services.user import UserService

users_router = APIRouter()


@users_router.post("", response_model=User)
async def create_user(*, db: DbSession, user_in: UserCreate) -> Any:
    user_service = UserService(db)
    user = await user_service.create(obj=user_in)
    return user

