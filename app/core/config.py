from enum import Enum
import secrets
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_extra_types.color import Color

import string


class DBType(str, Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        env_prefix="UURU_",
    )

    ## SECURITY

    DEFAULT_ROOT_USER: str = "root"
    DEFAULT_ROOT_PASSWORD: str = "rootpasswd"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days

    ## NETWORK

    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    ## DATABASE

    DATABASE_TYPE: DBType = DBType.SQLITE

    DATABASE_PATH: str | None = "./database.sqlite3"

    DATABASE_SERVER: str | None = None
    DATABASE_PORT: int | None = 5432
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = ""
    DATABASE_DB: str | None = ""
    DATABASE_DB_TEST: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> PostgresDsn:
        if not self.POSTGRES_DB_TEST:
            return self.SQLALCHEMY_DATABASE_URI

        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB_TEST,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        match (self.DATABASE_TYPE):
            case DBType.SQLITE:
                return f"sqlite:///{self.DATABASE_PATH}"
            case DBType.POSTGRES:
                return MultiHostUrl.build(
                    scheme="postgresql+psycopg",
                    username=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_SERVER,
                    port=self.DATABASE_PORT,
                    path=self.DATABASE_DB,
                )
            case DBType.MYSQL:
                return MultiHostUrl.build(
                    scheme="mysql+pymysql",
                    username=self.DATABASE_USER,
                    password=self.DATABASE_PASSWORD,
                    host=self.DATABASE_SERVER,
                    port=self.DATABASE_PORT,
                    path=self.DATABASE_DB,
                    charset="utf8mb4",
                )

    ## BEHAVIOR

    ENVIRONMENT: Literal["local", "production"] = "local"
    LIFESPAN_DROP_DB: bool = False

    ## TELEPHONE

    EXTENSION_DIGITS: int = 4
    EXTENSION_PASSWORD_LENGTH: int = 20
    EXTENSION_PASSWORD_CHARS: str = string.digits

    EXTENSION_TOKEN_PREFIX: str = "01990"
    EXTENSION_TOKEN_LENGTH: int = 8

    ## SITE

    SITE_NAME: str = "Default"
    SITE_SLOGAN: str = "You can configure this!"
    SHOW_SITE_SLOGAN: bool = True

    PRIMARY_COLOR: Color = "#75ff40"
    SECONDARY_COLOR: Color = "#450b6f"


settings = Settings()
