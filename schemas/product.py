from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    name: str
    price: float
    quantity: int
    model_config = ConfigDict(from_attributes=True)
