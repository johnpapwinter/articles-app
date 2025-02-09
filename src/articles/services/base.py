from typing import TypeVar, Generic, Type, Optional, Literal

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.core.error_messages import ErrorMessages
from src.articles.db.base import Base
from src.articles.repositories.base import BaseRepository

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    owner_field: Optional[Literal["owner_id", "user_id"]] = None

    def __init__(self, repository: Type[RepositoryType], db: AsyncSession):
        self.repository = repository(db)
        self.db = db

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        """
        find an object by its id
        :param obj_id: the id of the object in question
        :return: the object or None
        """
        obj = await self.repository.get_by_id(obj_id)
        if not obj:
            raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND.value)
        return obj

    async def create(self, *, obj: CreateSchemaType) -> ModelType:
        """
        create a new object in the database
        :param obj: the object to be created
        :return: the created object
        """
        async with self.db.begin_nested():
            return await self.repository.create(obj_in=obj)

    async def update(self, *, obj_id: int, obj: UpdateSchemaType, user_id: int) -> ModelType:
        """
        update an object in the database
        :param obj_id: the id of the object in question
        :param obj: the object to be updated
        :param user_id: the id of the user attempting to update the object
        :return: the updated object
        """
        async with self.db.begin_nested():
            db_obj = await self.repository.get_by_id(obj_id)
            if self.owner_field:
                await self._check_ownership(db_obj=db_obj, user_id=user_id)

            return await self.repository.update(db_obj=db_obj, obj_in=obj)

    async def delete(self, *, obj_id: int, user_id: int) -> ModelType:
        """
        delete an object in the database
        :param obj_id: the id of the object in question
        :param user_id: the id of the user attempting to delete the object
        :return: the deleted object
        """
        async with self.db.begin_nested():
            db_obj = await self.repository.get_by_id(obj_id)
            if self.owner_field:
                await self._check_ownership(db_obj=db_obj, user_id=user_id)

            return await self.repository.delete(obj_id=obj_id)

    async def _check_ownership(self, *, db_obj: ModelType, user_id: int) -> None:
        """Check whether the owner of the object is in fact the user attempting to perform the operation"""
        if not self.owner_field:
            return

        obj_owner_id = getattr(db_obj, self.owner_field)
        if obj_owner_id != user_id:
            raise HTTPException(status_code=403, detail=ErrorMessages.NOT_AUTHORIZED_TO_MODIFY.value)
