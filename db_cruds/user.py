from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_cruds.base import DBConnectorBase
from models.all_models import User

from schemas.user import UserCreateForDB, UserUpdate


class DBUserOps(DBConnectorBase[User, UserCreateForDB, UserUpdate]):
    """User crud"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_user_by_email(self, user_email: str) -> Optional[User]:
        """
        Get user model by email

        :param user_email: user email
        :return: found user model instance or None
        """
        result = await self._db.execute(
            select(self.model)
            .where(self.model.email == user_email)
        )
        return result.scalars().first()
