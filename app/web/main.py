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
