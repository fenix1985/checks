from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.config import settings
from core.enums import PaymentType
from db_cruds.check import DBCheckOps
from db_cruds.product import DBProductCheckOps
from db_cruds.user import DBUserOps
from schemas.user import UserRegisterQuery, UserLoginQuery
from security.auth_connector import AuthConnector


async def test_list_of_checks_created_by_user(
        db: AsyncSession,
        client: AsyncClient,
        auth_connector: AuthConnector,
        crud_user: DBUserOps,
        crud_check: DBCheckOps,
        crud_product_check: DBProductCheckOps,
) -> None:
    """This test checks creation of a check by authorized user"""

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

    await auth_connector.register(UserRegisterQuery(**payload))

    user = await crud_user.get_user_by_email(user_email=email)
    assert user is not None
    credentials = {"user_email": email, "password": password}
    token = await auth_connector.login(UserLoginQuery(**credentials))

    checks = await crud_check.get_list()
    assert len(checks) == 0

    product_details = await crud_product_check.get_list()
    assert len(product_details) == 0

    product_payload = {
        "name": "some product",
        "price": 20,
        "quantity": 2
    }
    payment_payload = {
        "type": PaymentType.CASH,
        "amount": 40
    }
    payload = {
        "products": [product_payload],
        "payment": payment_payload
    }

    register_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(register_url, json=payload,  headers={"Authorization": f"Bearer {token.access_token}"})

    assert response.status_code == status.HTTP_201_CREATED
    resp = response.json()

    product_payload02 = {
        "name": "A",
        "price": 150,
        "quantity": 3
    }
    payment_payload02 = {
        "type": PaymentType.CASHLESS,
        "amount": 450
    }

    payload02 = {
        "products": [product_payload02],
        "payment": payment_payload02
    }

    register_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(register_url, json=payload02,  headers={"Authorization": f"Bearer {token.access_token}"})

    assert response.status_code == status.HTTP_201_CREATED
    resp02 = response.json()

    register_url = f"{settings.API_PREFIX}/checks/my-checks?total_sum=200&page=1&size=20"
    response = await client.get(register_url,  headers={"Authorization": f"Bearer {token.access_token}"})

    assert response.status_code == status.HTTP_200_OK
    resp = response.json()

