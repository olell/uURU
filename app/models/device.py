"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from datetime import datetime
from typing import Optional, Self
import uuid
from pydantic import Field, model_validator
from sqlmodel import JSON, Column, Relationship, SQLModel

from app.models.extension import Extension
from app.telephoning.main import Telephoning

from pydantic import (
    ValidationError,
)

class Device(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.UUID, primary_key=True)
    device_id: str = Field(unique=True)

    name: str
    type: str
    description: str

    extension: Optional["Extension"] = Relationship(back_populates="devices")
    extension_id: Optional[str] = Field(default=None, foreign_key="extension.extension")

    extra_fields: dict = Field(default_factory=dict, sa_column=Column(JSON))

    last_seen: Optional[datetime] = None

    @model_validator(mode="after")
    def check_phone_flavor(self) -> Self:
        if self.type not in Telephoning.get_all_phone_types():
            raise ValidationError(f"Unknown phone type: {self.type}")

        flavor = Telephoning.get_flavor_by_type(self.type)
        if flavor.EXTRA_FIELDS is not None:
            print(flavor, flavor.EXTRA_FIELDS)
            flavor.EXTRA_FIELDS.model_validate(self.extra_fields)

        return self

    def get_extra_field(self, key):
        return self.extra_fields.get(key, None)