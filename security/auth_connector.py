from fastapi import HTTPException
from starlette import status

from security.token_handler import TokenHandler
from db_cruds.user import DBUserOps
from models.all_models import User

from schemas.token import TokenBase, TokenType
from schemas.user import UserRegisterQuery, UserBase, UserCreateForDB, UserLoginQuery
from utils import verify_secret, get_password_hash


class AuthConnector:
    """
    Authorization methods
    """

    def __init__(self, db_connector: DBUserOps, token_handler: TokenHandler):
        self.__db_connector = db_connector
        self.__token_handler = token_handler

    async def register(self, auth_details: UserRegisterQuery) -> UserBase:
        """
        Register a user

        :param auth_details: registration query parameter
        :return: The registered user as sqlalchemy's model instance.
        """

        # create user
        hashed_password = get_password_hash(auth_details.password)

        user: User = await self.__db_connector.create(
            obj_in=UserCreateForDB(
                register_query=auth_details,
                hashed_password=hashed_password,
            )
        )

        return UserBase.model_validate(user)

    async def login(self, auth_details: UserLoginQuery) -> TokenBase:
        """
        Login user

        :param auth_details: login query parameter
        :return: The authorization jwt tokens.
        """
        existing_user = await self.__db_connector.get_user_by_email(auth_details.user_email)

        if (existing_user is None) or (
            not verify_secret(auth_details.password, existing_user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email and/or password",
            )

        return self._generate_tokens(existing_user.user_id)

    async def refresh_token(self, refresh_token: str) -> TokenBase:
        """
        Generate refresh token

        :param refresh_token: refresh token
        :return: The new tokens to perform authorization.
        """
        payload = self.__token_handler.decode_token(refresh_token, token_type=TokenType.AUTH_REFRESH)
        user_id = int(payload["sub"])

        existing_user = await self.__db_connector.get_or_raise_404(user_id)
        return self._generate_tokens(existing_user.user_id)

    def _generate_tokens(self, user_id: int) -> TokenBase:
        """
        Generate tokens for user with given user_id

        :param user_id: The user unique identity
        :return: The new tokens to perform authorization.
        """
        access_token, access_token_expiry_date = self.__token_handler.encode_token(TokenType.AUTH_ACCESS, user_id)
        refresh_token, refresh_token_expiry_date = self.__token_handler.encode_token(TokenType.AUTH_REFRESH, user_id)

        return TokenBase(
            **{
                "user_id": user_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_token_expiry_date": access_token_expiry_date,
                "refresh_token_expiry_date": refresh_token_expiry_date,
            }
        )
