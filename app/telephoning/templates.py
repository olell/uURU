"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Any

from urllib.request import Request
from fastapi.templating import Jinja2Templates

from app.core.config import settings


def app_context(request: Request) -> dict[str, Any]:
    return {
        "app": request.app,
        "settings": settings.model_dump(),
    }


templates = Jinja2Templates(
    directory="templates/telephoning", context_processors=[app_context]
)
