from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.db import SessionDep
from app.models.user import UserRole
from app.web.deps import OptionalCurrentUser
from app.web.message import Message, MessageBroker
from app.web.templates import templates
from app.models.crud.extension import filter_extensions_by_name

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
def index():
    return "/phonebook"


@router.get("/phonebook", response_class=HTMLResponse)
def phonebook(
    *,
    session: SessionDep,
    request: Request,
    query: str | None = None,
    user: OptionalCurrentUser,
):
    public = True
    if user is not None and user.role == UserRole.ADMIN:
        public = False
    phonebook_data = filter_extensions_by_name(session, user, query, public)
    return templates.TemplateResponse(
        request=request,
        name="phonebook.j2.html",
        context={"user": user, "phonebook": phonebook_data, "query": query},
    )


@router.get("/map", response_class=HTMLResponse)
def phonemap(
    *,
    session: SessionDep,
    request: Request,
    user: OptionalCurrentUser,
):
    public = True
    if user is not None and user.role == UserRole.ADMIN:
        public = False
    phonebook_data = filter_extensions_by_name(session, user, None, public)
    return templates.TemplateResponse(
        request=request,
        name="phonemap.j2.html",
        context={"user": user, "phonebook": phonebook_data},
    )


@router.get("/error/{status_code}")
def error(request: Request, status_code: Optional[int] = None):
    return templates.TemplateResponse(
        request, "error.j2.html", {"status_code": status_code}
    )
