from datetime import datetime, UTC, timedelta

from jose import jwt, JWTError
from pydantic import ValidationError

from src.articles.auth.schemas import TokenPayload
from src.articles.core.config import settings


def create_access_token(user_id: int) -> str:
    """Create JWT access token for specific user"""
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "issuer": settings.JWT_ISSUER,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    }

    return jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> TokenPayload:
    """Verify JWT access token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenPayload(**payload)
        return token_data
    except (JWTError, ValidationError):
        raise ValueError("Invalid token")


