from typing import Optional, TYPE_CHECKING

from sqlmodel import Relationship, SQLModel, Field
from pydantic import BaseModel

import uuid

if TYPE_CHECKING:
    from app.models.user import User

from app.core.config import settings


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


class ExtensionCreate(BaseModel):
    extension: str = Field(
        min_length=settings.EXTENSION_DIGITS,
        max_length=settings.EXTENSION_DIGITS,
        regex=f"^\d{{{settings.EXTENSION_DIGITS}}}$",
    )
    name: str
    public: bool


class TemporaryExtensions(SQLModel, table=True):
    extension: str = Field(unique=True, primary_key=True)
    password: str
    uid: int
    ppn: int
