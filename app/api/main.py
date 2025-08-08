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
