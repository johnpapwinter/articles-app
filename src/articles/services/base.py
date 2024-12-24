from typing import TypeVar, Generic, Type, Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.db.base import Base
from src.articles.repositories.base import BaseRepository

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(self, repository: Type[RepositoryType], db: AsyncSession):
        self.repository = repository(db)

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        obj = await self.repository.get_by_id(obj_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

    async def create(self, *, obj: CreateSchemaType) -> ModelType:
        return await self.repository.create(obj_in=obj)

    async def update(self, *, obj_id: int, obj: UpdateSchemaType) -> ModelType:
        db_obj = await self.repository.get_by_id(obj_id)
        return await self.repository.update(db_obj=db_obj, obj_in=obj)

    async def delete(self, *, obj_id: int) -> ModelType:
        return await self.repository.delete(obj_id=obj_id)

