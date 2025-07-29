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
    directory="templates_provisioning", context_processors=[app_context]
)
