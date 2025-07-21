from fastapi import APIRouter

from app.api import user

router = APIRouter()
router.include_router(user.router)
