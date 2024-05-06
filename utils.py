import uuid
from datetime import datetime, timezone

from passlib.context import CryptContext

from core.config import settings
from schemas.token import TokenType


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def camelcase_to_snake(word: str) -> str:
    """
    Convert camelcase to snakecase
    """
    return "".join(["_" + c.lower() if c.isupper() else c for c in word]).lstrip("_")


def utcnow() -> datetime:
    """
    Get now date in UTC
    """
    return datetime.now(timezone.utc)


def random_token() -> str:
    """
    Generate random string and return it's hex representation

    :return: random string
    """
    return uuid.uuid4().hex


def get_expire_date(token_type: TokenType):

    expire_date_maper = {
        TokenType.AUTH_ACCESS: settings.API_ACCESS_TOKEN_EXPIRY_TIME_IN_MINUTES,
        TokenType.AUTH_REFRESH: settings.API_REFRESH_TOKEN_EXPIRY_TIME_IN_MINUTES
    }
    return expire_date_maper[token_type]


def get_password_hash(password: str) -> str:
    """
    Hash password

    :param password: password to hash
    :return: hashed password
    """
    return pwd_context.hash(password)


def verify_secret(plain_secret: str, hashed_password: str) -> bool:
    """
    Verify password

    :param plain_secret: password to verify
    :param hashed_password: hashed password
    :return: True if verification succeed, otherwise False
    """
    return pwd_context.verify(plain_secret, hashed_password)