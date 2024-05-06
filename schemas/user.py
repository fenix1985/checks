from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, root_validator, ConfigDict


class UserBase(BaseModel):

    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserLoginQuery(BaseModel):

    user_email: str
    password: str


class RegisterBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserRegisterQuery(RegisterBase):
    password: str


class UserCreateForDB(RegisterBase):
    hashed_password: str

    def __init__(self, *, register_query: Optional[UserRegisterQuery] = None, **data):
        if register_query is not None:
            data.update(
                first_name=register_query.first_name,
                last_name=register_query.last_name,
                email=register_query.email,
            )
        super().__init__(**data)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserOut(UserBase):

    created: datetime
    model_config = ConfigDict(from_attributes=True)
