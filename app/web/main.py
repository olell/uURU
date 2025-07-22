from fastapi import APIRouter

from app.web.routes import index
from app.web.routes import user
from app.web.routes import extension

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
router.include_router(user.router)
router.include_router(extension.router)
