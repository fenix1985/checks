import datetime
from typing import Dict

from httpx import AsyncClient
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from security.auth_connector import AuthConnector
from core.config import settings
from db_cruds.user import DBUserOps
from schemas.user import UserRegisterQuery, UserBase


async def test_user_register_flow(
    db: AsyncSession,
    client: AsyncClient,
    crud_user: DBUserOps
) -> None:
    """This test checks user registrations workflow"""

    email = "test@test.com"
    password = "12356789"

    payload = {
        "first_name": "Борис",
        "last_name": "Джонсонюк",
        "email": email,
        "password": password,
    }
    searched_user = await crud_user.get_user_by_email(email)
    assert searched_user is None
    register_url = f"{settings.API_PREFIX}/auth/register/"

    response = await client.post(register_url, json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    resp = response.json()
    payload.pop("password")

    for field in payload.keys():
        assert payload[field] == resp[field]

    registered_user = await crud_user.get_user_by_email(email)
    assert registered_user is not None

    for field in payload.keys():
        assert payload[field] == getattr(registered_user, field)

    login_url = f"{settings.API_PREFIX}/auth/login/"
    user_login = {"user_email": email, "password": password}

    # login user
    response = await client.post(login_url, json=user_login)
    assert response.status_code == status.HTTP_200_OK
    resp = response.json()
    assert resp["user_id"] == registered_user.user_id
    assert resp["access_token"]
    assert resp["refresh_token"]
    assert resp["access_token_expiry_date"]
    assert resp["refresh_token_expiry_date"]


async def test_unregistered_user_login(
        db: AsyncSession,
        client: AsyncClient,
        auth_connector: AuthConnector,
        crud_user: DBUserOps
) -> None:
    """This test checks user registrations workflow"""

    email = "test@test.com"
    searched_user = await crud_user.get_user_by_email(email)
    assert searched_user is None

    # try login should fail
    login_url = f"{settings.API_PREFIX}/auth/login/"
    user_login = {"user_email": email, "password": "123"}
    response = await client.post(login_url, json=user_login)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


