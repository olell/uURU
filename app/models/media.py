"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, TYPE_CHECKING
import uuid
from pydantic import BaseModel, computed_field
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.extension import Extension
    from app.models.user import User


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    RAW = "raw"


class ImageFormat(BaseModel):
    # please note: the out_type literal format must match util.media.SUPPORTED_IMAGE_FORMATS
    out_type: Literal["avif", "bmp", "gif", "jpeg", "png", "tiff", "webp"] = "png"
    colormode: Literal["1", "L", "RGB"] = "RGB"
    width: Optional[int] = None
    height: Optional[int] = None


class AudioFormat(BaseModel):
    # please note: the out_type literal format must match util.media.SUPPORTED_AUDIO_FORMATS
    out_type: Literal["gsm", "wav", "ogg", "mp3", "flac"] = "mp3"
    samplerate: int = 44100
    channels: int = 2
    bitdepth: int = 16


class Media(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    type: MediaType

    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    created_by: Optional["User"] = Relationship(back_populates="media")

    uploaded_at: datetime = Field(default_factory=datetime.now)

    stored_as: str

    assigned_extensions: list["ExtensionMedia"] = Relationship(back_populates="media")


class ExtensionMedia(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # this refers to the key of the MEDIA dict in the phoneflavor of the extension
    name: str

    media_id: Optional[uuid.UUID] = Field(default=None, foreign_key="media.id")
    media: Optional[Media] = Relationship(back_populates="assigned_extensions")

    extension_id: Optional[str] = Field(default=None, foreign_key="extension.extension")
    extension: Optional["Extension"] = Relationship(back_populates="assigned_media")
