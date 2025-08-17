"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_extra_types.color import Color

from app.core.config import PublicSettings, settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/")
def get_settings() -> PublicSettings:
    return settings
