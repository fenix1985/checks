from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from security.auth_connector import AuthConnector

from security.token_handler import TokenHandler
from core.session import async_session, run_transaction
from db_cruds.check import DBCheckOps
from db_cruds.product import DBProductCheckOps
from db_cruds.user import DBUserOps


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with run_transaction(session):
            yield session


def get_user_crud(session: AsyncSession = Depends(get_session)) -> DBUserOps:
    return DBUserOps(session)


def get_check_crud(session: AsyncSession = Depends(get_session)) -> DBCheckOps:
    return DBCheckOps(session)


def get_product_check_crud(session: AsyncSession = Depends(get_session)) -> DBProductCheckOps:
    return DBProductCheckOps(session)


def get_token_handler() -> TokenHandler:
    return TokenHandler()


def get_auth_connector(
    crud: DBUserOps = Depends(get_user_crud),
    token_handler: TokenHandler = Depends(get_token_handler),
) -> AuthConnector:
    return AuthConnector(crud, token_handler)


