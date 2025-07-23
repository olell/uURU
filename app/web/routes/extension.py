from typing import Annotated
from fastapi import APIRouter, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.db import SessionDep
from app.web.deps import CurrentUser
from app.web.templates import templates
from app.models.extension import ExtensionCreate
from app.models.crud.extension import create_extension

router = APIRouter(prefix="/extension")


@router.get("/own", response_class=HTMLResponse)
def get_own_extensions(
    request: Request, session: SessionDep, current_user: CurrentUser
):

    return templates.TemplateResponse(
        request, "extension/own.j2.html", {"user": current_user}
    )


@router.get("/create", response_class=HTMLResponse)
def create_extension_page(request: Request, current_user: CurrentUser):
    return templates.TemplateResponse(
        request, "extension/create.j2.html", {"user": current_user}
    )


@router.post(
    "/create", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def create_extension_handle(
    session: SessionDep, data: Annotated[ExtensionCreate, Form()], user: CurrentUser
):
    try:
        create_extension(session, user, data)
    except:
        # todo information about error
        return "/extension/create"
    return "/extension/own"
