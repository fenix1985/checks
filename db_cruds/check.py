from typing import Union, Dict, Any, Optional, List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db_cruds.base import DBConnectorBase, CreateSchemaType, ModelType
from db_cruds.queries import BASE_CHECK_GET_QUERY, COUNT_TOTAL_AND_REST_QUERY, BASE_CHECK_GET_LIST_QUERY
from models.all_models import Check, ProductCheck
from schemas.check import CheckOrderInput, UpdateCheck, CheckOut, Payment
from schemas.product import Product


class DBCheckOps(DBConnectorBase[Check, CheckOrderInput, UpdateCheck]):

    def __init__(self, db: AsyncSession):
        super().__init__(db, Check)

    @staticmethod
    async def convert_schema_to_dict(check_order: CreateSchemaType) -> Dict[str, Any]:
        order_dict = check_order.model_dump()
        return order_dict

    async def create_check(self, check: Check) -> ModelType:
        """
        Create model instance from its blueprint

        :param check: blueprint check
        :return: created model instance
        """

        self._db.add(check)
        await self._db.flush([check])
        return check

    async def get_user_checks_with_details(self, customer_id: int, filters: Optional[Dict[Any, Any]]) -> List[CheckOut]:
        """
        Fetches multiple records from the database of a given model (ModelType).

        :param customer_id:
        :param filters: Dictionary of filters to apply.
            The str name of model field and appropriate value to filter by it

        :returns: List of model instances.
        """
        query = BASE_CHECK_GET_LIST_QUERY.where(Check.customer_id == customer_id)

        if filters:
            if total_sum := filters["total_sum"]:
                query = query.having(func.sum(ProductCheck.price*ProductCheck.quantity) > total_sum)

            if payment_type := filters["payment_type"]:
                query = query.filter(Check.type == payment_type)

            if greater_than_date := filters["greater_than_date"]:
                query = query.filter(Check.created_at == greater_than_date)

        result = (await self._db.execute(query)).unique().all()

        checks_out = []

        for check, total_sum, payment_rest, check_creator in result:
            checks_out.append(
                self._convert_base_query_result_to_check_schema(check, total_sum, payment_rest, check_creator=check_creator)
            )
        return checks_out


    async def get_with_collected_details(
            self,
            customer_id: Optional[int] = None,
            check_id: Optional[int] = None,
            check_token: Optional[str] = None
    ) -> Union[CheckOut, None]:

        count_query = COUNT_TOTAL_AND_REST_QUERY.where(Check.customer_id == customer_id) if customer_id else COUNT_TOTAL_AND_REST_QUERY
        query = BASE_CHECK_GET_QUERY.where(Check.customer_id == customer_id) if customer_id else BASE_CHECK_GET_QUERY

        if check_id:
            query = query.where(Check.check_id == check_id)
            count_query = count_query.where(Check.check_id == check_id)
        elif check_token:
            query = query.where(Check.token == check_token)
            count_query = count_query.where(Check.token == check_token)
        else:
            return

        count_result = (await self._db.execute(count_query)).unique().one_or_none()

        if count_result:
            result = (await self._db.execute(query)).unique().one_or_none()
            return self._convert_base_query_result_to_check_schema(
                check=result[0],
                check_creator=result[1],
                total_check_sum=count_result[1],
                payment_rest=count_result[2]
            )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The object with primary key {check_id} could not be found.")

    @staticmethod
    def _convert_base_query_result_to_check_schema(
            check: Check,
            total_check_sum: float,
            payment_rest: float,
            check_creator: Optional[str] = None,
    ) -> CheckOut:
        payment_info = Payment.model_validate(check)
        product_info = [Product.model_validate(e) for e in check.details]
        check_out = CheckOut(
            payment=payment_info,
            products=product_info,
            check_id=check.check_id,
            created_at=check.created_at,
            token=check.token,
            url=check.url,
            total=total_check_sum,
            rest=payment_rest,
            customer_name=check_creator if check_creator else f"{check.customer.first_name}" + f"{check.customer.last_name}"
        )
        return check_out
