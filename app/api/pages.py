import os
from logging import getLogger
from pathlib import Path

import mistune
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/pages", tags=["pages"])
logger = getLogger(__name__)


def get_page_files() -> list[str] | None:
    if not settings.ENABLE_PAGES:
        return None

    if not os.path.exists("pages/"):
        return None

    files = os.listdir("pages/")
    md_files = list(filter(lambda f: f.endswith(".md"), files))

    return md_files


@router.get("/")
def get_pages() -> dict[str, str]:
    files = get_page_files()
    if files is None:
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
            logger.error(f"Failed to render page {page}: {e!s}")

    return response
