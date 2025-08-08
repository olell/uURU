"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_extra_types.color import Color

from app.core.config import settings

router = APIRouter(prefix="/site", tags=["site"])


class SiteInfo(BaseModel):
    site_name: str
    site_slogan: str
    show_site_slogan: bool


@router.get("/")
def get_site_info() -> SiteInfo:
    return SiteInfo(
        site_name=settings.SITE_NAME,
        site_slogan=settings.SITE_SLOGAN,
        show_site_slogan=settings.SHOW_SITE_SLOGAN,
    )
