from typing import Any

from urllib.request import Request
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.web.message import MessageBroker


def app_context(request: Request) -> dict[str, Any]:
    return {
        "app": request.app,
        "settings": settings.model_dump(),
        "msgbroker": MessageBroker
    }


templates = Jinja2Templates(directory="templates", context_processors=[app_context])
