from fastapi import APIRouter

from app.web import index
from app.web import user

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
router.include_router(user.router)
