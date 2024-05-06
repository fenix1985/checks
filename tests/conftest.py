import asyncio
from typing import AsyncGenerator


import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from db_cruds.check import DBCheckOps
from db_cruds.product import DBProductCheckOps
from security.auth_connector import AuthConnector
from security.token_handler import TokenHandler
from core.session import async_session
from db_cruds.user import DBUserOps
from deps import get_auth_connector, get_user_crud, get_token_handler, get_session, get_check_crud, \
    get_product_check_crud
from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator:
    async with async_session() as session:
        transaction = await session.begin()
        yield session
        await transaction.rollback()


@pytest.fixture(scope="function")
def auth_handler() -> AuthConnector:
    return get_auth_connector()


@pytest.fixture(scope="function")
def token_handler() -> TokenHandler:
    return get_token_handler()


@pytest.fixture(scope="function")
def crud_user(db: AsyncSession) -> DBUserOps:
    return get_user_crud(db)


@pytest.fixture(scope="function")
def crud_check(db: AsyncSession) -> DBCheckOps:
    return get_check_crud(db)


@pytest.fixture(scope="function")
def crud_product_check(db: AsyncSession) -> DBProductCheckOps:
    return get_product_check_crud(db)


@pytest.fixture(scope="function")
def auth_connector(
    crud_user: DBUserOps,
    token_handler: TokenHandler,
) -> AuthConnector:
    return get_auth_connector(crud_user, token_handler)


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator:
    app.dependency_overrides[get_session] = lambda: db

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test.example/") as async_client:
            yield async_client
