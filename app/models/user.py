"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel

from enum import Enum

import uuid

from app.models.extension import Extension


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
