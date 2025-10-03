"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi import status
from pydantic import BaseModel

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.core.db import SessionAsteriskDep
from app.models.user import UserRole
from app.telephoning.flavor import MediaDescriptor
from app.telephoning.main import Telephoning
from app.core.config import settings
from app.telephoning.websip import WebSIPExtension, WebSIPManager


router = APIRouter(prefix="/telephoning", tags=["telephoning"])


class PhoneType(BaseModel):
    schema: Optional[dict] = None
    display_index: int
    name: str
    max_extension_name_chars: int
    media: dict[str, MediaDescriptor]


@router.get("/types")
def get_phone_types(user: CurrentUser) -> list[PhoneType]:
    schemas: list[PhoneType] = []
    for flavor in Telephoning.instance().flavors.values():
        if flavor.is_public() or user.role == UserRole.ADMIN:
            for phone_type in flavor.PHONE_TYPES:
                pt = PhoneType(
                    schema=flavor.get_schema(),
                    display_index=flavor.DISPLAY_INDEX,
                    name=phone_type,
                    max_extension_name_chars=flavor.MAX_EXTENSION_NAME_CHARS,
                    media=flavor.MEDIA,
                )
                schemas.append(pt)
    return schemas


@router.get("/websip")
def create_websip(
    session_asterisk: SessionAsteriskDep, user: OptionalCurrentUser
) -> WebSIPExtension:
    if not settings.ENABLE_WEBSIP:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="WebSIP is disabled"
        )

    if user is None and not settings.WEBSIP_PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="WebSIP is only available for logged in users",
        )

    extension = WebSIPManager.instance().create_extension(session_asterisk, user)

    return extension


@router.delete("/websip")
def delete_websip(session_asterisk: SessionAsteriskDep, extension: str, password: str):
    if not settings.ENABLE_WEBSIP:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="WebSIP is disabled"
        )

    ext = WebSIPManager.instance().get_extension(extension)
    if ext.auth_pass != password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password for extension"
        )

    WebSIPManager.instance().delete_extension(session_asterisk, ext)

    return {}


@router.put("/websip", status_code=status.HTTP_204_NO_CONTENT)
def put_websip(extension: str):
    if not settings.ENABLE_WEBSIP:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="WebSIP is disabled"
        )

    ext = WebSIPManager.instance().get_extension(extension)
    ext.last_seen = datetime.now()

    return {}
