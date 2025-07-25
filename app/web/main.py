from fastapi import APIRouter

from app.web.routes import index
from app.web.routes import user
from app.web.routes import extension
from app.web.routes import admin

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
router.include_router(user.router)
router.include_router(extension.router)
router.include_router(admin.router)