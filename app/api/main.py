"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from fastapi import APIRouter

from app.api import extension, federation, media, pages, settings, telephoning, user

router = APIRouter()
router.include_router(user.router)
router.include_router(extension.router)
router.include_router(settings.router)
router.include_router(telephoning.router)
router.include_router(pages.router)
router.include_router(federation.router)
router.include_router(media.router)
