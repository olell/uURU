"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from fastapi import APIRouter

from app.api import user
from app.api import extension
from app.api import site
from app.api import telephoning

router = APIRouter()
router.include_router(user.router)
router.include_router(extension.router)
router.include_router(site.router)
router.include_router(telephoning.router)
