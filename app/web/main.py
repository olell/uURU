"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from fastapi import APIRouter

from app.web.routes import index
from app.web.routes import user
from app.web.routes import extension
from app.web.routes import admin
from app.web.routes import pages

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
router.include_router(user.router)
router.include_router(extension.router)
router.include_router(admin.router)
router.include_router(pages.router)
