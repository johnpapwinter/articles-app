import os
from datetime import datetime, UTC, timedelta

from jose import jwt, JWTError
from pydantic import ValidationError

from src.articles.auth.schemas import TokenPayload
from src.articles.core.config.factory import get_settings

# from src.articles.core.config import settings


settings = get_settings(os.getenv("ENVIRONMENT", "development"))


def create_access_token(user_id: int) -> str:
    """Create JWT access token for specific user"""
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iss": settings.JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)).timestamp()),
    }

    return jwt.encode(
        payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> TokenPayload:
    """Verify JWT access token and return payload"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], issuer=settings.JWT_ISSUER
        )

        token_data = TokenPayload(sub=int(payload["sub"]))
        return token_data
    except (JWTError, ValidationError) as e:
        raise ValueError(f"Invalid token: {str(e)}")


