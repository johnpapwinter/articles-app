from typing import Any

from fastapi import APIRouter, HTTPException

from src.articles.api.deps import DbSession
from src.articles.schemas.user import UserSchema, UserCreate
from src.articles.services.user import UserService
from src.articles.utils.decorators import endpoint_decorator

users_router = APIRouter()


@users_router.post("", response_model=UserSchema)
@endpoint_decorator(
    summary="Create new user",
    status_code=201,
    response_model=UserSchema,
    description="Create a new user",
)
async def create_user(*, db: DbSession, user_in: UserCreate) -> Any:
    try:
        user_service = UserService(db)
        user = await user_service.create(obj=user_in)
        if user is None:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
