from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from app.core.db import SessionDep
from app.web.deps import CurrentUser
from app.web.templates import templates

router = APIRouter(prefix="/extension")


@router.get("/own")
def get_own_extensions(
    request: Request, session: SessionDep, current_user: CurrentUser
):

    return templates.TemplateResponse(
        request, "extension/own.j2.html", {"user": current_user}
    )
