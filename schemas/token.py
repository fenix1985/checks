import enum
from datetime import datetime

from pydantic import BaseModel


class TokenType(enum.Enum):
    AUTH_REFRESH = 1
    AUTH_ACCESS = 2


class TokenQuery(BaseModel):
    token: str


class TokenBase(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    access_token_expiry_date: datetime
    refresh_token_expiry_date: datetime

