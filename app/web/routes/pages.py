"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
import os
from fastapi import APIRouter, HTTPException, Request, status
import string

import mistune

from app.web.templates import templates

router = APIRouter(prefix="/pages")
logger = getLogger(__name__)


@router.get("/{name}")
def get_page(request: Request, name: str):

    if not set(str(name)) <= set(string.ascii_letters + string.digits + " "):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Page name contains invalid characters"
        )

    page_file = os.path.join("pages", str(name) + ".md")
    if not os.path.isfile(page_file):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        with open(page_file, "r") as target:
            content = target.read()
    except Exception as e:
        logger.error(f"Failed reading page file {page_file}: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Failed reading page")

    logger.info(f"Rendering page {name} from {page_file}!")
    html = mistune.html(content)

    return templates.TemplateResponse(request, "page.j2.html", {"content": html})
