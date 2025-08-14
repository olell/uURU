"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from enum import Enum
import random
import string
from typing import Optional, TYPE_CHECKING, Self, Any

from sqlmodel import JSON, Column, Relationship, SQLModel, Field
from pydantic import (
    BaseModel,
    ValidationError,
    computed_field,
    model_validator,
    field_validator,
    Field as PydanticField,
)
import json
import uuid
from urllib.parse import unquote

from app.telephoning.main import Telephoning


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

    public: bool = False
    type: str

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
        if self.lat is None:
            return None
        return self.lat / 10000000

    @property
    def lon_float(self) -> float:
        if self.lon is None:
            return None
        return self.lon / 10000000


class Extension(ExtensionBase, table=True):
    # store only in database, don't expose
    token: str
    password: str
    info: str

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="extensions")

    extra_fields: dict = Field(default_factory=dict, sa_column=Column(JSON))

    def get_flavor_model(self) -> BaseModel:
        flavor = Telephoning.get_flavor_by_type(self.type)
        if flavor is None or flavor.EXTRA_FIELDS is None:
            return None

        return flavor.EXTRA_FIELDS.model_validate(self.extra_fields)

    @model_validator(mode="after")
    def check_phone_flavor(self) -> Self:
        if not self.type in Telephoning.get_all_phone_types():
            raise ValidationError(f"Unknown phone type: {self.type}")

        flavor = Telephoning.get_flavor_by_type(self.type)
        if flavor.EXTRA_FIELDS is not None:
            print(flavor, flavor.EXTRA_FIELDS)
            flavor.EXTRA_FIELDS.model_validate(self.extra_fields)

    def get_extra_field(self, key):
        return self.extra_fields.get(key, None)


class ExtensionCreate(BaseModel):
    extension: str = PydanticField(
        min_length=settings.EXTENSION_DIGITS,
        max_length=settings.EXTENSION_DIGITS,
        pattern=rf"^\d{{{settings.EXTENSION_DIGITS}}}$",
    )
    name: str
    info: str
    public: bool = Field(default=False)
    type: str
    extra_fields: dict = {}

    location_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    # required if the model is parsed from form data where a checked
    # checkbox will only set the key, but not a value ("")
    @field_validator("public", mode="before")
    @classmethod
    def validate_checkbox(cls, value: Any) -> Any:
        return True if value == "" else value

    @field_validator("extra_fields", mode="before")
    @classmethod
    def validate_extra_fields_json(cls, value: Any):
        print("validating extra fields")
        print(value, type(value))
        if not isinstance(value, str):
            return value

        if value.strip().startswith("%7B"):
            value = unquote(value)

        return json.loads(value)


class ExtensionUpdate(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    public: Optional[bool] = False

    location_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    extra_fields: dict = {}

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

    @field_validator("extra_fields", mode="before")
    @classmethod
    def validate_extra_fields_json(cls, value: Any):
        print("validating extra fields")
        print(value, type(value))
        if not isinstance(value, str):
            return value

        if value.strip().startswith("%7B"):
            value = unquote(value)

        return json.loads(value)


class TemporaryExtensions(SQLModel, table=True):
    extension: str = Field(unique=True, primary_key=True)
    password: str
    uid: int
    ppn: int

    def generate_extension() -> int:
        return int(
            "9"
            + "".join(
                [
                    random.choice(string.digits)
                    for _ in range(settings.EXTENSION_DIGITS * 2)
                ]
            )
        )
