"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import TYPE_CHECKING, Literal, Optional
from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel

from enum import Enum

from datetime import datetime
import uuid

from app.models.extension import Extension
from pydantic import model_validator


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserBase(SQLModel):
    username: str = Field(unique=True)
    role: UserRole = Field(default=UserRole.USER)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str

    extensions: list[Extension] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str = Field(min_length=10, max_length=100)
    invite: str | None = None


class InviteVariant(str, Enum):
    COUNT = "count"
    TIME = "time"
    TIME_AND_COUNT = "time+count"


class Invite(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    invite: str = Field(min_length=10, max_length=10)
    variant: InviteVariant = InviteVariant.COUNT

    use_count: Optional[int] = None
    max_uses: Optional[int] = None
    valid_until: Optional[datetime] = None

    @model_validator(mode="after")
    def check_variant_fields(self):
        if self.variant == InviteVariant.COUNT:
            if self.use_count is None or self.max_uses is None:
                raise ValueError(
                    "use_count and max_uses must be set when variant is 'count'"
                )
        elif self.variant == InviteVariant.TIME:
            if self.valid_until is None:
                raise ValueError("valid_until must be set when variant is 'time'")
        elif self.variant == InviteVariant.TIME_AND_COUNT:
            if (
                self.use_count is None
                or self.max_uses is None
                or self.valid_until is None
            ):
                raise ValueError(
                    "use_count, max_uses and valid_until must be set when variant is 'time and count'"
                )
        return self

    def is_valid(self):
        # conditions depending on variant:
        # COUNT: use_count < max_uses
        # TIME: valid_until after now
        # TIME_AND_COUNT: valid_until after now and use_count < max_uses
        return not (
            (self.variant == InviteVariant.COUNT and self.use_count >= self.max_uses)
            or (
                self.variant == InviteVariant.TIME and self.valid_until < datetime.now()
            )
            or (
                self.variant == InviteVariant.TIME_AND_COUNT
                and (
                    self.valid_until < datetime.now() or self.use_count >= self.max_uses
                )
            )
        )

    def use(self):
        if (
            self.variant == InviteVariant.COUNT
            or self.variant == InviteVariant.TIME_AND_COUNT
        ):
            self.use_count += 1


class InviteCreate(BaseModel):
    variant: InviteVariant
    max_uses: Optional[int] = None
    valid_days: Optional[int] = None
    valid_hours: Optional[int] = None

    @model_validator(mode="after")
    def check_variant_fields(self):
        if self.variant == InviteVariant.COUNT:
            if self.max_uses is None:
                raise ValueError("max_uses must be set when variant is 'count'")
        elif self.variant == InviteVariant.TIME:
            if self.valid_days is None or self.valid_hours is None:
                raise ValueError(
                    "valid_days and valid_hours must be set when variant is 'time'"
                )
        elif self.variant == InviteVariant.TIME_AND_COUNT:
            if (
                self.max_uses is None
                or self.valid_days is None
                or self.valid_hours is None
            ):
                raise ValueError(
                    "max_uses, valid_days and valid_hours must be set when varaint is 'time and count'"
                )
        return self


class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    role: UserRole | None = None


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=10, max_length=100)
    new_password: str = Field(min_length=10, max_length=100)


class Token(BaseModel):
    token: str


class TokenPayload(BaseModel):
    exp: int
    sub: str
