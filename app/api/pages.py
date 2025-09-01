from logging import getLogger
import os
from pathlib import Path
from fastapi import APIRouter
import mistune

from app.web.pages import available, get_all

router = APIRouter(prefix="/pages", tags=["pages"])
logger = getLogger(__name__)


@router.get("/")
def get_pages() -> dict[str, str]:
    files = available(True)
    if not files:
        return {}

    response = {}

    for page in files:
        try:
            page_file = os.path.join("pages", page)
            with open(page_file, "r") as target:
                content = target.read()
            rendered = mistune.html(content)
            response.update({Path(page).stem: rendered})
        except Exception as e:
            logger.error(f"Failed to render page {page}: {str(e)}")

    return response
