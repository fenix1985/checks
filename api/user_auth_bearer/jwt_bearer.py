from datetime import timedelta
from typing import Dict, Optional, Tuple, Union, Any

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from security.token_handler import TokenHandler
from core.config import settings
from db_cruds.user import DBUserOps
from deps import get_user_crud
from schemas.token import TokenType
from utils import get_expire_date, utcnow


class BaseJWTBearer(HTTPBearer):
    """
    JWT Bearer authorization
    """

    def __init__(
        self,
        auth_handler: Optional[TokenHandler] = None,
        required_token_type: Optional[TokenType] = None,
    ):
        # auto_error=True allow raise 403 response if credentials is None
        super(BaseJWTBearer, self).__init__(auto_error=True)
        self._auth_handler = auth_handler
        self._required_token_type = required_token_type

    def _parse_payload(self, credentials: str) -> Tuple[int, int]:
        payload = self._auth_handler.decode_token(credentials)
        try:
            token_type = payload["token_type"]
            token_owner = int(payload["sub"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

        return token_type, token_owner

    def _check_token_type(self, token_type: int):
        if self._required_token_type and token_type != self._required_token_type.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token type")


class JWTBearer(BaseJWTBearer):
    """
    JWT Bearer authorization
    """

    def __init__(
        self,
        auth_handler: TokenHandler,
        required_token_type: Optional[TokenType] = None,
    ):
        super(JWTBearer, self).__init__(auth_handler, required_token_type=required_token_type)

    async def __call__(self, request: Request, user_crud: DBUserOps = Depends(get_user_crud)):

        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        token_type, user_id = self._parse_payload(credentials.credentials)
        self._check_token_type(token_type)

        user = await user_crud.get(user_id)
        return user
