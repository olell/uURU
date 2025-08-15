"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.models.user import UserRole
from app.telephoning.main import Telephoning


router = APIRouter(prefix="/telephoning", tags=["telephoning"])


class PhoneType(BaseModel):
    schema: Optional[dict] = None
    display_index: int
    name: str


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
                )
                schemas.append(pt)
    return schemas
