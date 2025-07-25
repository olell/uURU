from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.db import SessionDep
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
    phonebook_data = filter_extensions_by_name(session, user, query)
    return templates.TemplateResponse(
        request=request,
        name="phonebook.j2.html",
        context={"user": user, "phonebook": phonebook_data, "query": query},
    )
