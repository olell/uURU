from logging import INFO, getLevelNamesMapping
import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_extra_types.color import Color

import string


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
    WEB_PREFIX: str = ""
    API_V1_STR: str = "/api/v1"
    TELEPHONING_PREFIX: str = "/telephoning"

    WEB_HOST: str = "127.0.0.1:8000"
    ASTERISK_HOST: str = "127.0.0.1"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    ## DATABASE

    DATABASE_TYPE: Literal["mysql"] | Literal["postgres"] = "postgres"
    DATABASE_SERVER: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str = ""
    DATABASE_DB: str = ""
    DATABASE_DB_TEST: str | None = None

    ASTERISK_DATABASE_SERVER: str
    ASTERISK_DATABASE_PORT: int = 3306
    ASTERISK_DATABASE_USER: str
    ASTERISK_DATABASE_PASSWORD: str
    ASTERISK_DATABASE_DB: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> str:
        if not self.DATABASE_DB_TEST:
            return self.SQLALCHEMY_DATABASE_URI

        return str(
            MultiHostUrl.build(
                scheme=(
                    "postgresql+psycopg"
                    if self.DATABASE_TYPE == "postgres"
                    else "mysql+pymysql"
                ),
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_SERVER,
                port=self.DATABASE_PORT,
                path=self.DATABASE_DB_TEST,
            )
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme=(
                    "postgresql+psycopg"
                    if self.DATABASE_TYPE == "postgres"
                    else "mysql+pymysql"
                ),
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_SERVER,
                port=self.DATABASE_PORT,
                path=self.DATABASE_DB,
            )
        )

    @computed_field
    @property
    def SQLACLCHEMY_ASTERISK_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="mysql+pymysql",
                username=self.ASTERISK_DATABASE_USER,
                password=self.ASTERISK_DATABASE_PASSWORD,
                host=self.ASTERISK_DATABASE_SERVER,
                port=self.ASTERISK_DATABASE_PORT,
                path=self.ASTERISK_DATABASE_DB,
            )
        )

    ## BEHAVIOR

    LOGLEVEL: Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    ENVIRONMENT: Literal["local", "production"] = "local"
    LIFESPAN_DROP_DB: bool = False

    @computed_field
    @property
    def logging_loglevel(self) -> int:
        return getLevelNamesMapping().get(self.LOGLEVEL, INFO)

    ## TELEPHONE

    EXTENSION_DIGITS: int = 4
    EXTENSION_PASSWORD_LENGTH: int = 20
    EXTENSION_PASSWORD_CHARS: str = string.digits

    EXTENSION_TOKEN_PREFIX: str = "01990"
    EXTENSION_TOKEN_LENGTH: int = 8

    RESERVED_EXTENSIONS: list[int | tuple[int, int]] = []
    ALL_EXTENSION_TYPES_PUBLIC: bool = 0

    # normal users may not add extension beginning with any string of this list
    RESERVED_NAME_PREFIXES: list[str] = []

    # list of enabled phone flavors, should contains the names of
    # files in "app/telephoning/phonetypes/" without the .py suffix
    ENABLED_PHONE_FLAVORS: list[str] = ["sip"]

    ## SITE

    SITE_NAME: str = "Default"
    SITE_SLOGAN: str = "You can configure this!"
    SHOW_SITE_SLOGAN: bool = True
    SITE_LAT: float = 0
    SITE_LON: float = 0

    ENABLE_PAGES: bool = True
    PAGES_TITLE: str = "Pages"

    OMM_HOST: str | None = None
    OMM_PORT: int = 12621
    OMM_USER: str = "omm"
    OMM_PASSWORD: str | None = None

    GRANDSTREAM_WIFI_SSID: str | None = None
    GRANDSTREAM_WIFI_PASSWD: str | None = None


settings = Settings()
