from datetime import date
from typing import Any, Union, Optional

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from pydantic import ValidationError
from starlette import status
from fastapi.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from api.user_auth_bearer.deps import token_access
from core.enums import PaymentType
from core.validation_messages import NOT_ENOUGH_MONEY
from db_cruds.check import DBCheckOps
from deps import get_check_crud
from models.all_models import User, ProductCheck, Check
from schemas.check import CheckOrderInput, CheckOut, Payment
from schemas.product import Product

from utils import random_token

router = APIRouter(prefix="/checks", tags=["Checks"])


@router.post(
    "/",
    summary="Create check",
    description="Create a check",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckOut,
)
async def create_check(
        request: Request,
        check_order: CheckOrderInput,
        current_user: User = Depends(token_access()),
        check_ops: DBCheckOps = Depends(get_check_crud)

) -> Any:
    """
    Create a check using the given payload.
    """
    prepared_data = await check_ops.convert_schema_to_dict(check_order)

    products_in_check = prepared_data.pop("products")
    total_products_cost = 0

    products_instances = []
    for product in products_in_check:
        products_instances.append(ProductCheck(**product))
        total_products_cost += product["price"]*product["quantity"]

    if prepared_data["payment"]["amount"] < total_products_cost:
        raise ValidationError(NOT_ENOUGH_MONEY)

    check_unique_token = random_token()
    prepared_data["payment"]["token"] = check_unique_token
    prepared_data["payment"]["customer_id"] = current_user.user_id
    prepared_data["payment"]["url"] = str(request.url_for("public_check", token=check_unique_token))

    check = Check(**prepared_data["payment"])
    check.details.extend(products_instances)
    check = await check_ops.create_check(check)

    payment_info = Payment.model_validate(check)
    product_info = [Product.model_validate(e) for e in check.details]

    return CheckOut(
        payment=payment_info,
        products=product_info,
        check_id=check.check_id,
        created_at=check.created_at,
        token=check.token,
        url=check.url,
        total=total_products_cost,
        rest=prepared_data["payment"]["amount"]-total_products_cost,
        customer_name=f"{current_user.first_name} {current_user.last_name}"
    )


@router.get(
    "/my-checks",
    summary="List of all checks created by a user",
    description="Get checks created by a user",
    response_model=Page[CheckOut]
)
async def get_customer_checks(
        greater_than_date: Union[date, None] = None,
        total_sum: Optional[float] = None,
        payment_type: Optional[PaymentType] = None,
        current_user: User = Depends(token_access()),
        check_ops: DBCheckOps = Depends(get_check_crud),
) -> Any:
    """
    Getting the list of all checks created by curren user
    """

    query_params = dict(greater_than_date=greater_than_date, total_sum=total_sum, payment_type=payment_type)
    result = await check_ops.get_user_checks_with_details(customer_id=current_user.user_id, filters=query_params)
    return paginate(result)


@router.get(
    "/{check_id}",
    summary="Get check created by user",
    description="Get a check created by a user",
    response_model=CheckOut,
)
async def get_check_by_id(
        check_id: int,
        current_user: User = Depends(token_access()),
        check_ops: DBCheckOps = Depends(get_check_crud),
) -> Any:
    """
    Getting the check with specified check id by registered user
    """
    return await check_ops.get_with_collected_details(customer_id=current_user.user_id, check_id=check_id)


templates = Jinja2Templates(directory="static/templates")


@router.get(
    "/{token}/show-public",
    summary="Get check info for public",
    description="Get users",
    response_class=HTMLResponse,
    name="public_check"
)
async def get_check_by_token(
        request: Request,
        token: str,
        check_ops: DBCheckOps = Depends(get_check_crud),
) -> Any:
    """
    Sending html page with all check details. Can be accessed any unauthorized user
    """

    check = await check_ops.get_with_collected_details(check_token=token)
    check_data = check.model_dump()

    for key in ["check_id", "token", "url"]:
        check_data.pop(key)

    return templates.TemplateResponse(
        request=request,
        name="invoice.html",
        context={"check_data": check_data, "payment_map": {PaymentType.CASH: "Готівка", PaymentType.CASHLESS: "Карта"}}
    )
