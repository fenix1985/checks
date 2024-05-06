from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from db_cruds.base import DBConnectorBase
from models.all_models import User

from schemas.user import UserCreateForDB, UserUpdate


class DBUserOps(DBConnectorBase[User, UserCreateForDB, UserUpdate]):
    """User crud"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_user_by_email(self, user_email: str, relations: Optional[List[str]] = None) -> Optional[User]:
        """
        Get user model by email

        :param user_email: user email
        :param relations: List of child relationships names as string
            attributes to join as outer left join.
        :return: found user model instance or None
        """
        result = await self._db.execute(
            select(User)
            # .options(*[joinedload(field) for field in relations] if relations else [])
            .where(self.model.email == user_email)
        )
        return result.scalars().first()
