from typing import Optional

from fastapi import Header, HTTPException, Depends
from jose import JWTError

from src.articles.api.deps import DbSession
from src.articles.auth.jwt_utils import verify_token
from src.articles.models import User
from src.articles.services.user import UserService


async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authorized")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Not authorized")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Not authorized")


async def get_current_user(db: DbSession, token: str = Depends(get_token_from_header)) -> User:
    try:
        payload = verify_token(token)
        user_id: int = payload.sub
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not authorized")
    except (JWTError, ValueError) as e:
        raise HTTPException(status_code=401, detail=f"Not authorized {str(e)}")

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")

    return user


