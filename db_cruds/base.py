from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from starlette import status

from models.base import BaseClass

ModelType = TypeVar("ModelType", bound=BaseClass)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class DBConnectorBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD object with default methods to Create, Read, Update, Delete (CRUD).
    """

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.model = model
        self._db = db

    async def get(self, object_pk: Any, relations: Optional[List[str]] = None) -> Optional[ModelType]:
        """
        Get model instance.

        :param object_pk: primary key id of object
        :param relations: List of child relationships names as string
            attributes to join as outer left join.
        :return: found model instance or None
        """
        query = (
            select(self.model)
            .options(*[joinedload(field) for field in relations] if relations else [])
            .filter(self.model.pk() == object_pk)
        )
        result = await self._db.execute(query)
        return result.scalars().first()

    async def get_or_raise_404(self, object_pk: Any, relations: Optional[List[str]] = None) -> ModelType:
        """
        Get model instance or raise 404 NotFound exception when not found.

        :param object_pk: primary key id of object
        :param relations: List of child relationships names as string
            attributes to join as outer left join.
        :return: found model instance
        """
        obj = await self.get(object_pk, relations)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"The object with primary key {object_pk} could not be found.")
        return obj

    async def get_list(
        self, relations: Optional[List[ModelType]] = None, filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Fetches multiple records from the database of a given model (ModelType).

        :param relations: List of child relationships names as string
            attributes to join as outer left join.
        :param filters: Dictionary of filters to apply.
            The str name of model field and appropriate value to filter by it

        :returns: List of model instances.
        """

        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)

        if relations:
            query = query.options(*[joinedload(field) for field in relations])

        result = await self._db.execute(query)
        return result.unique().scalars().all()

    async def _convert_schema_to_dict(
        self,
        obj: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> Dict[str, Any]:
        return obj if isinstance(obj, dict) else obj.model_dump(exclude_unset=True)


    async def validate_db_object(self, db_obj: ModelType):
        """
        Validate database model's object before adding to db.

        :param db_obj: Database model to validate
        """

    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Create model instance from its blueprint

        :param obj_in: blueprint object
        :return: created model instance
        """
        obj_in_data = await self._convert_schema_to_dict(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        await self.validate_db_object(db_obj)
        self._db.add(db_obj)
        await self._db.flush([db_obj])
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update model instance from its blueprint

        :param db_obj: model instance that is updated
        :param obj_in: blueprint object
        :return: updated model instance
        """
        update_data = await self._convert_schema_to_dict(obj_in)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        await self.validate_db_object(db_obj)
        self._db.add(db_obj)
        await self._db.flush([db_obj])
        return db_obj

    async def drop(self, object_pk: int):
        """
        Remove model instance

        :param object_pk: primary key of object that is deleted
        """
        query = delete(self.model).where(self.model.pk() == object_pk)
        await self._db.execute(query)

    async def drop_many(self, object_ids: List[int]):
        """
        Remove model instance

        :param object_ids: primary keys of objects that are deleted
        """
        query = delete(self.model).where(self.model.pk().in_(object_ids))
        await self._db.execute(query)
