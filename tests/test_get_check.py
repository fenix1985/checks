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

    create_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(create_url, json=payload,  headers={"Authorization": f"Bearer {token.access_token}"})

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
    await client.post(
        create_url, json=payload_02,  headers={"Authorization": f"Bearer {token_02.access_token}"}
    )

    # Now we have created 2 checks by 2 different users
    # Let's check getting unique user_01's getting check
    first_user_check_id = resp["check_id"]
    url_to_get_check_by_id = f"{settings.API_PREFIX}/checks/{first_user_check_id}"
    response = await client.get(url_to_get_check_by_id,  headers={"Authorization": f"Bearer {token.access_token}"})

    assert response.status_code == status.HTTP_200_OK
    first_user_check_in_response = response.json()
    assert first_user_check_in_response["check_id"] == first_user_check_id

    payment_data_response_user_01 = first_user_check_in_response.pop("payment")
    # We check matching of payment data which is in the payload and the response
    for field in payment_payload.keys():
        assert payment_payload[field] == payment_data_response_user_01[field]

    product_details_response_user_01 = resp.pop("products")
    # We check matching of products data which are in the payload and the response
    for product_in_response in product_details_response_user_01:
        for field in product_payload.keys():
            assert product_payload[field] == product_in_response[field]

    # We test getting data for check created by firs user
    assert first_user_check_in_response["check_id"] == first_user_check_id
    assert datetime.fromisoformat(first_user_check_in_response["created_at"]) is not None
    assert first_user_check_in_response["token"] is not None
    assert first_user_check_in_response["url"] is not None
    total_sum_to_pay_user_01 = product_payload["price"] * product_payload["quantity"]
    assert first_user_check_in_response["total"] == total_sum_to_pay_user_01
    assert first_user_check_in_response["rest"] == total_sum_to_pay_user_01 - payment_payload["amount"]

    # Also let's test getting user_01's check by authorized user_02
    url_to_get_check_by_id = f"{settings.API_PREFIX}/checks/{first_user_check_id}"
    response = await client.get(url_to_get_check_by_id,  headers={"Authorization": f"Bearer {token_02.access_token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_check_by_not_authenticated_user(
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

    credentials = {"user_email": email, "password": password}
    token_01 = await auth_connector.login(UserLoginQuery(**credentials))

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

    create_url = f"{settings.API_PREFIX}/checks/"
    response = await client.post(create_url, json=payload,  headers={"Authorization": f"Bearer {token_01.access_token}"})
    resp_01 = response.json()
    # this endpoint already tested, so we trust it.

    # Now we have created 2 checks by 2 different users
    # Let's check getting unique user_01's check
    first_user_check_id = resp_01["check_id"]
    url_to_get_check_by_id = f"{settings.API_PREFIX}/checks/{first_user_check_id}"
    response = await client.get(url_to_get_check_by_id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED






