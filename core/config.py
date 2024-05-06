import secrets
from typing import Optional, Dict, Any

from pydantic.v1 import BaseSettings, validator, PostgresDsn


class Settings(BaseSettings):

    API_PREFIX: str = "/api"
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_ACCESS_TOKEN_EXPIRY_TIME_IN_MINUTES: int = 2*60
    API_REFRESH_TOKEN_EXPIRY_TIME_IN_MINUTES: int = 24 * 60

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    INITIALIZE_DB: bool
    DATA_DIRECTORY_PATH: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:

        case_sensitive = True
        extra = "allow"


settings = Settings()
