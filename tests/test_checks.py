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


async def test_get_check_by_creator(
        db: AsyncSession,
        client: AsyncClient,
        auth_connector: AuthConnector,
        crud_user: DBUserOps,
        crud_check: DBCheckOps,
        crud_product_check: DBProductCheckOps,
) -> None:

    email = "test@test.com"
    password = "12356789"

    user_data_payload = {
        "first_name": "Борис",
        "last_name": "Джонсонюк",
        "email": email,
        "password": password,
    }

    await auth_connector.register(UserRegisterQuery(**user_data_payload))
    user01 = await crud_user.get_user_by_email(user_email=email)

    credentials = {"user_email": email, "password": password}
    token = await auth_connector.login(UserLoginQuery(**credentials))


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
    # this endpoint already tested, so we trust it.

    email_02 = "test_02@test.com"
    password_02 = "985764321"

    user_data_payload_02 = {
        "first_name": "Nikolas",
        "last_name": "Septemberus",
        "email": email_02,
        "password": password_02,
    }

    await auth_connector.register(UserRegisterQuery(**user_data_payload_02))
    user_02 = await crud_user.get_user_by_email(email_02)

    credentials_02 = {"user_email": email_02, "password": password_02}
    token_02 = await auth_connector.login(UserLoginQuery(**credentials_02))

    product_payload_02 = {
        "name": "A",
        "price": 150,
        "quantity": 3
    }
    payment_payload_02 = {
        "type": PaymentType.CASHLESS,
        "amount": 450
    }

    payload_02 = {
        "products": [product_payload_02],
        "payment": payment_payload_02
    }

    register_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(register_url, json=payload_02,  headers={"Authorization": f"Bearer {token_02.access_token}"})

    assert response.status_code == status.HTTP_201_CREATED
    resp_02 = response.json()

    first_user_check_id = resp["check_id"]

    register_url = f"{settings.API_PREFIX}/checks/{first_user_check_id}"
    response = await client.get(register_url,  headers={"Authorization": f"Bearer {token.access_token}"})

    assert response.status_code == status.HTTP_200_OK
    first_user_check_in_response = response.json()
    assert first_user_check_in_response["check_id"] == first_user_check_id
