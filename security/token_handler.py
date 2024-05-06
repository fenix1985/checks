from datetime import timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException
from starlette import status

from core.config import settings
from schemas.token import TokenType
from utils import utcnow, get_expire_date


# class TokenHandler:
#     """
#     Token and password verification handler.
#     """
#
#     def __init__(self):
#         self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#         self.__hashed_secret = settings.SECRET_KEY
#
#     def encode_token(self, token_type: TokenType, identity_id: int):
#         """
#         Encode token
#
#         :param token_type: type of token
#         :param identity_id: user identity
#         :return:
#         """
#         datetime_now = utcnow()
#         expiry_date = get_expire_date(token_type)
#         payload = {
#             "exp": expiry_date,
#             "iat": datetime_now,
#             "sub": identity_id,
#             "token_type": token_type.value,
#         }
#         token = jwt.encode(payload, self.__hashed_secret, algorithm=settings.ALGORITHM)
#
#         return token, expiry_date
#
#     def decode_token(self, token: str, token_type: Optional[TokenType] = None):
#         """
#         Decode token
#
#         :param token: encoded token
#         :param token_type: type of token
#         :return: decoded token payload
#         """
#         try:
#             payload = jwt.decode(token, self.__hashed_secret, algorithms=[settings.ALGORITHM])
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature has expired")
#         except jwt.InvalidTokenError:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         except Exception as e:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
#         else:
#             if token_type:
#                 if payload["token_type"] != token_type.value:
#                     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#             return payload
#
#     def verify_password(self, plain_password, hashed_password) -> bool:
#         """
#         Verify password
#
#         :param plain_password: password to verify
#         :param hashed_password: hashed password
#         :return: True if verification succeed, otherwise False
#         """
#         return self.pwd_context.verify(plain_password, hashed_password)
#
#     def get_password_hash(self, password) -> str:
#         """
#         Hash password
#
#         :param password: password to hash
#         :return: hashed password
#         """
#         return self.pwd_context.hash(password)


class TokenHandler:
    """
    Token and password verification handler.
    """

    def encode_token(
        self, token_type: TokenType, identity_id: int
    ):
        """
        Encode token

        :param token_type: type of token
        :param identity_id: user identity
        :return: (token, expiry_date)
        """

        payload = self.build_token_pyload(token_type, identity_id)
        token = self.build_token(payload)
        return token, payload["exp"]

    def decode_token(self, token: str, token_type: Optional[TokenType] = None):
        """
        Decode token

        :param token: encoded token
        :param token_type: type of token
        :raises: HTTPException when get_payload raises any exception.
        :return: decoded token payload
        """
        try:
            payload = self.extract_payload_from_token(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        else:
            if token_type and token_type.value != payload["token_type"]:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            return payload

    @staticmethod
    def get_expire_date(token_type: TokenType):
        """
        This method inherited by child classes and allow to get
            expiration date for a provided token type.
        :param token_type: encoded token
        :raises: KeyError exception when TOKEN_TYPE_EXPIRY_DELTA_IN_MINUTES
                dict does not have provided token_type
        """
        return utcnow() + timedelta(minutes=get_expire_date(token_type))

    def build_token_pyload(
        self, token_type: TokenType, identity_id: int
    ):
        """
        The method allows to build a jwt payload based on provided input parameters.

        :param token_type: The type of token
        :param identity_id: The identity of auth subject.

        """
        payload = {
            "exp": self.get_expire_date(token_type),
            "iat": utcnow(),
            "sub": identity_id,
            "token_type": token_type.value,
        }
        return payload

    @staticmethod
    def extract_payload_from_token(token: str) -> Dict[str, Any]:
        """
        The method decodes a token and returns payload of this token.
        :param token: The str token to be decoded.
        :returns: dict object with climes.
        """
        return jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    @staticmethod
    def build_token(payload: Dict[str, Any]) -> str:
        """
        The method encodes a token from a payload and returns it.
        :param payload: The dict object to encode into the token.
        :returns: the jwt token.
        """
        return jwt.encode(payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)