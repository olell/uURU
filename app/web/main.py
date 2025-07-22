from fastapi import APIRouter

from app.web import index

router = APIRouter(tags=["webinterface"])
router.include_router(index.router)
