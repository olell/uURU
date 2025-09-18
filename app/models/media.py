"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    RAW = "raw"


class Media(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    type: MediaType

    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    created_by: Optional[User] = Relationship(back_populates="assets")

    uploaded_at: datetime = Field(default_factory=datetime.now)
