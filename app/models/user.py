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
    password: str | None = Field(min_length=10, max_length=100, default=None)
    role: UserRole | None = None


class Token(BaseModel):
    token: str


class TokenPayload(BaseModel):
    exp: int
    sub: str
