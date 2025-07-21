from fastapi import APIRouter

from app.api import user
from app.api import extension

router = APIRouter()
router.include_router(user.router)
router.include_router(extension.router)
