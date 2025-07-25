from enum import Enum
from typing import Optional, TYPE_CHECKING, Self, Any

from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel, model_validator, field_validator
from pydantic_extra_types.mac_address import MacAddress

import uuid

if TYPE_CHECKING:
    from app.models.user import User

from app.core.config import settings


class ExtensionType(str, Enum):
    SIP = "SIP"
    DECT = "DECT"
    INNOVAPHONE_241 = "Innovaphone 241"
    INNOVAPHONE_201A = "Innovaphone 201a"


class ExtensionBase(SQLModel):
    extension: str = Field(unique=True, primary_key=True)
    name: str


class Extension(ExtensionBase, table=True):
    # store only in database, don't expose
    token: str
    password: str
    info: str
    public: bool = False

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="extensions")

    type: ExtensionType
    mac: Optional[MacAddress] = None

    # TODO: should throw http error - not 500 and stack trace
    @model_validator(mode="after")
    def verify_mac_set(self) -> Self:
        if self.type in [
            ExtensionType.SIP,
            ExtensionType.DECT,
        ]:
            return self

        if not self.mac:
            raise ValueError("mac needs to be defined if innovaphone")

        return self


class ExtensionCreate(BaseModel):
    extension: str = Field(
        min_length=settings.EXTENSION_DIGITS,
        max_length=settings.EXTENSION_DIGITS,
        regex=f"^\d{{{settings.EXTENSION_DIGITS}}}$",
    )
    name: str
    info: str
    public: bool = Field(default=False)
    type: ExtensionType
    mac: Optional[MacAddress] = None

    # required if the model is parsed from form data where a checked
    # checkbox will only set the key, but not a value ("")
    @field_validator("public", mode="before")
    @classmethod
    def validate_checkbox(cls, value: Any) -> Any:
        return True if value == "" else value


class ExtensionUpdate(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    public: Optional[bool] = None
    type: Optional[ExtensionType] = None


    # required if the model is parsed from form data where a checked
    # checkbox will only set the key, but not a value ("")
    @field_validator("public", mode="after")
    @classmethod
    def validate_checkbox(cls, value: Any) -> Any:
        if value is None:
            return False
        else:
            return value



class TemporaryExtensions(SQLModel, table=True):
    extension: str = Field(unique=True, primary_key=True)
    password: str
    uid: int
    ppn: int
