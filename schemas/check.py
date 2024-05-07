from datetime import datetime
from typing import List, Optional, Annotated

from annotated_types import Len
from pydantic import BaseModel, ConfigDict, conlist

from core.enums import PaymentType
from schemas.product import Product


class Payment(BaseModel):

    type: PaymentType
    amount: float
    model_config = ConfigDict(from_attributes=True)


class CheckOrderInput(BaseModel):

    products: Annotated[List[Product], Len(min_length=1)]
    payment: Payment
    model_config = ConfigDict(from_attributes=True)


class UpdateCheck(BaseModel):
    pass


class CheckOut(CheckOrderInput):

    check_id: int
    created_at: datetime
    token: str
    url: str
    total: float
    rest: float
    customer_name: Optional[str] = None









