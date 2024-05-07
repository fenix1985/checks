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


async def test_create_check_by_not_authorized_user(
        db: AsyncSession,
        client: AsyncClient,
        auth_connector: AuthConnector,
        crud_user: DBUserOps,
        crud_check: DBCheckOps,
        crud_product_check: DBProductCheckOps,
) -> None:
    """This test checks creation of a check by not authorized user"""

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
        "amount": 5
    }
    payload = {
        "products": [product_payload],
        "payment": payment_payload
    }
    register_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(register_url, json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    checks = await crud_check.get_list()
    assert len(checks) == 0

    product_details = await crud_product_check.get_list()
    assert len(product_details) == 0


async def test_create_check(
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

    payment_data_response = resp.pop("payment")
    # We check matching of payment data which is in the payload and the response
    for field in payment_payload.keys():
        assert payment_payload[field] == payment_data_response[field]

    product_details_response = resp.pop("products")
    # We check matching of products data which are in the payload and the response
    for product_in_response in product_details_response:
        for field in product_payload.keys():
            assert product_payload[field] == product_in_response[field]

    checks = await crud_check.get_list()
    assert len(checks) == 1
    created_check = checks[0]

    assert created_check.check_id == resp["check_id"]
    assert datetime.fromisoformat(resp["created_at"]) is not None
    assert created_check.token == resp["token"] and created_check.token
    assert created_check.url == resp["url"] and created_check.url

    check_products_details = created_check.details
    assert len(created_check.details) == 1

    for field in payment_payload:
        assert payment_payload[field] == getattr(created_check, field)

    # We check matching between products data which are saved in database and the payload
    for saved_product_check in check_products_details:
        for field in product_payload.keys():
            assert payload["products"][0][field] == getattr(saved_product_check, field)


async def test_create_check_without_products(
        db: AsyncSession,
        client: AsyncClient,
        auth_connector: AuthConnector,
        crud_user: DBUserOps,
        crud_check: DBCheckOps,
        crud_product_check: DBProductCheckOps,
) -> None:
    """This test checks validation on creation of a check by authorized user"""

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
    payment_payload = {
        "type": PaymentType.CASH,
        "amount": 40
    }
    payload = {
        "payment": payment_payload
    }
    register_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(register_url, json=payload,  headers={"Authorization": f"Bearer {token.access_token}"})

    payload["products"] = []

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp = response.json()
    assert resp["detail"][0]["loc"] == ['body', 'products']
    assert resp["detail"][0]["msg"] == 'Field required'

    response = await client.post(register_url, json=payload,  headers={"Authorization": f"Bearer {token.access_token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp = response.json()
    assert resp["detail"][0]["loc"] == ['body', 'products']
    assert resp["detail"][0]['msg'] == "List should have at least 1 item after validation, not 0"
