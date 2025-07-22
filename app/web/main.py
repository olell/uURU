from fastapi import APIRouter

from app.web.routes import index
from app.web.routes import user

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
router.include_router(user.router)
