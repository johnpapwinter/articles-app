from fastapi import APIRouter, HTTPException

from src.articles.api.deps import DbSession
from src.articles.auth.jwt_utils import create_access_token
from src.articles.auth.schemas import Token, LoginCredentials
from src.articles.services.user import UserService

auth_router = APIRouter()


@auth_router.post('/login', response_model=Token)
async def login(db: DbSession, credentials: LoginCredentials) -> Token:
    user_service = UserService(db)
    user = await user_service.authenticate(username=credentials.username, password=credentials.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token = create_access_token(user_id=user.id)

    return Token(access_token=token)

