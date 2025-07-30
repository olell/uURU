from enum import Enum
from typing import Optional, TYPE_CHECKING, Self, Any

from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel, model_validator, field_validator, Field as PydanticField

import uuid

if TYPE_CHECKING:
    from app.models.user import User

from app.core.config import settings

class ExtensionBase(SQLModel):
    extension: str = Field(unique=True, primary_key=True)
    name: str

    location_name: Optional[str] = None
    # stored as lat/lon * 10000000 ## todo: validator
    lat: Optional[int] = Field(default=None, ge=-900000000, le=900000000)
    lon: Optional[int] = Field(default=None, ge=-1800000000, le=1800000000)

    @field_validator("lat", "lon", mode="before")
    @classmethod
    def validate_latlon(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = float(value)
            if abs(value) > 180:
                value = int(value)

        if isinstance(value, float):
            return int(value * 10000000)
        if isinstance(value, int):
            return value

        raise ValueError("Lat / Lon must be an integer or float")

    @property
    def lat_float(self) -> float:
        if self.lat is None: return None
        return self.lat / 10000000

    @property
    def lon_float(self) -> float:
        if self.lon is None: return None
        return self.lon / 10000000


class Extension(ExtensionBase, table=True):
    # store only in database, don't expose
    token: str
    password: str
    info: str
    public: bool = False

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="extensions")

    type: str


class ExtensionCreate(BaseModel):
    extension: str = PydanticField(
        min_length=settings.EXTENSION_DIGITS,
        max_length=settings.EXTENSION_DIGITS,
        pattern=fr"^\d{{{settings.EXTENSION_DIGITS}}}$"
    )
    name: str
    info: str
    public: bool = Field(default=False)
    type: str

    location_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    # required if the model is parsed from form data where a checked
    # checkbox will only set the key, but not a value ("")
    @field_validator("public", mode="before")
    @classmethod
    def validate_checkbox(cls, value: Any) -> Any:
        return True if value == "" else value


class ExtensionUpdate(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    public: Optional[bool] = False

    location_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    @field_validator("lat", "lon", mode="before")
    @classmethod
    def validate_latlon(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = float(value)
            if abs(value) > 180:
                value = int(value)

        if isinstance(value, float):
            return int(value * 10000000)
        if isinstance(value, int):
            return value

        raise ValueError("Lat / Lon must be an integer or float")

    # required if the model is parsed from form data where a checked
    # checkbox will only set the key, but not a value ("")
    @field_validator("public", mode="before")
    @classmethod
    def validate_checkbox(cls, value: Any) -> Any:
        print(f"before '{value}'")
        if value is None:
            print("validated", False)
            return False
        else:
            print("Validated", True if value == "" else value)
            return True if value == "" else value


class TemporaryExtensions(SQLModel, table=True):
    extension: str = Field(unique=True, primary_key=True)
    password: str
    uid: int
    ppn: int
