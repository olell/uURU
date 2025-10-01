"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
import uuid
from pydantic import BaseModel, computed_field
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

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
    samplerate: Optional[int] = 44100
    channels: Optional[int] = 2
    bitdepth: Optional[int] = 16


class Media(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    type: MediaType

    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    created_by: Optional[User] = Relationship(back_populates="media")

    uploaded_at: datetime = Field(default_factory=datetime.now)

    default_format_json: dict = Field(default_factory=dict, sa_column=Column(JSON))

    @computed_field
    @property
    def default_format(self) -> AudioFormat | ImageFormat:
        if self.type == MediaType.IMAGE:
            return ImageFormat.model_validate(self.default_format_json)
        elif self.type == MediaType.AUDIO:
            return AudioFormat.model_validate(self.default_format_json)
        else:
            raise ValueError("Raw media does not have a default format!")
