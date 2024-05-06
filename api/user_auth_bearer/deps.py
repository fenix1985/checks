from api.user_auth_bearer.jwt_bearer import JWTBearer
from deps import get_token_handler
from schemas.token import TokenType


def token_access() -> JWTBearer:
    """
    This method allow everyone user access with any access role
    for target action function to handle input request.
    :returns: The instance of JWTBearer class to handle access permission.
    """
    return JWTBearer(
        auth_handler=get_token_handler(),
        required_token_type=TokenType.AUTH_ACCESS,
    )
