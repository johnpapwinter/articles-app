from typing import Optional

from pydantic import BaseModel

from src.articles.schemas.base import BaseSchema


class UserBase(BaseSchema):
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
