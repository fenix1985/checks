from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from core.enums import PaymentType
from schemas.product import Product


class Payment(BaseModel):

    type: PaymentType
    amount: float
    model_config = ConfigDict(from_attributes=True)


class CheckOrderInput(BaseModel):

    products: List[Product]
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









