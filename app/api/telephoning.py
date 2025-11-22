"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from asterisk.ami.response import FutureResponse
from logging import getLogger
from asterisk.ami.client import AMIClientAdapter
from app.models.crud.asterisk import get_contact
from app.core.db import SessionDep
from app.models.crud.extension import get_extension_by_id
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

logger = getLogger(__name__)

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


@router.get("/originate", status_code=status.HTTP_204_NO_CONTENT)
def originate_call(session: SessionDep, session_asterisk: SessionAsteriskDep, user: CurrentUser, source: str, dest: str):
    source_extension = get_extension_by_id(session, source, public=False)
    if source_extension is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source extension unknown")
    if source_extension.user_id != user.id and not user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You may not originate calls from this extension")
    
    contact = get_contact(session_asterisk, source_extension, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The source extension is offline")

    if not dest.isnumeric():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Destination must be a number!")

    client = Telephoning.instance().get_ami_client()
    adapter = AMIClientAdapter(client)
    response: FutureResponse = adapter.Originate(
        Channel=f"PJSIP/{source}",
        Exten=dest,
        Priority=1,
        Context="pjsip_internal"
    )

    logger.info(f"Originated call from {source} to {dest}")
    logger.debug(f"Received AMI response:\n{response.response}")

    if response is not None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="unable to originate call due to error from AMI")

    return {}