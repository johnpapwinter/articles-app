from typing import TypeVar, Generic, Type, Optional, Any, Dict

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.db.base import Base
from src.articles.utils.decorators import log_database_operations

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    @log_database_operations
    async def get_by_id(self, obj_id: Any) -> Optional[ModelType]:
        """
        get a database object by its id
        :param obj_id: the id of the object in question
        :return: the object or None if not found
        """
        query =select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @log_database_operations
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        create a new database object
        :param obj_in: the object to be created
        :return: the created object
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    @log_database_operations
    async def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]) -> ModelType:
        """
        update an existing database object
        :param db_obj: the object to be updated as it currently is in the database
        :param obj_in: the new object data that will be used to update the object
        :return: the updated object
        """
        obj_data = db_obj.to_dict()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    @log_database_operations
    async def delete(self, *, obj_id: int) -> ModelType:
        """
        delete a database object by its id
        :param obj_id: the id of the object in question
        :return: the deleted object
        """
        obj = await self.get_by_id(obj_id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj

    @log_database_operations
    async def get_by_name(self, name: str) -> Optional[ModelType]:
        """
        get a database object by its name (primarily used for the author and tag models)
        :param name: the name in question
        :return: the object found or None if not found
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

