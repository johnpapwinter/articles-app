from typing import Optional

from fastapi import Header, HTTPException, Depends
from jose import JWTError
from sqlalchemy.orm import Session

from src.articles.auth.jwt_utils import verify_token
from src.articles.core.error_messages import ErrorMessages
from src.articles.db import get_db
from src.articles.models import User
from src.articles.services.user import UserService


async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Get the JWT token from the authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail=ErrorMessages.NOT_AUTHORIZED.value)

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail=ErrorMessages.NOT_AUTHORIZED.value)
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail=ErrorMessages.NOT_AUTHORIZED.value)


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(get_token_from_header)) -> User:
    """This function returns the user of the JWT token"""
    try:
        payload = verify_token(token)
        user_id: int = payload.sub
        if user_id is None:
            raise HTTPException(status_code=401, detail=ErrorMessages.NOT_AUTHORIZED.value)
    except (JWTError, ValueError) as e:
        raise HTTPException(status_code=401, detail=ErrorMessages.NOT_AUTHORIZED.value)

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND.value)

    return user


