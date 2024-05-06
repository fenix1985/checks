from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from security.auth_connector import AuthConnector
from db_cruds.user import DBUserOps
from deps import get_auth_connector, get_user_crud
from models.all_models import User
from schemas.token import TokenBase, TokenQuery
from schemas.user import UserBase, UserRegisterQuery, UserLoginQuery

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post(
    "/register/",
    summary="Register user",
    description="Register a user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserBase,
)
async def register(
    auth_details: UserRegisterQuery,
    auth_connector: AuthConnector = Depends(get_auth_connector),
) -> UserBase:
    """
    Register a demo user and send verification email
    """
    return await auth_connector.register(auth_details)


@router.post(
    "/login/",
    summary="Login a user",
    description="Login a user and retrieve token",
    response_model=TokenBase,
)
async def login(
    auth_details: UserLoginQuery,
    auth_connector: AuthConnector = Depends(get_auth_connector),
) -> TokenBase:
    """
    Login a user and retrieve token
    """
    return await auth_connector.login(auth_details)


@router.post(
    "/refresh-token/",
    summary="Refresh access token",
    description="Refresh expired access token",
    response_model=TokenBase,
)
async def refresh_token(
    token_query: TokenQuery,
    auth_connector: AuthConnector = Depends(get_auth_connector),
) -> TokenBase:
    """
    Refresh expired access token
    """
    return await auth_connector.refresh_token(token_query.token)


@router.get(
    "/list/",
    summary="Get users",
    description="Get users",
    response_model=List[UserBase],
)
async def get_users(
    user_crud: DBUserOps = Depends(get_user_crud),
) -> List[User]:
    """
    Getting the list of all registered users
    """
    return await user_crud.get_list()
