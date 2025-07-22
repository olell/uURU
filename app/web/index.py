from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.web.deps import OptionalCurrentUser
from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
def index():
    return "/phonebook"


@router.get("/phonebook", response_class=HTMLResponse)
def phonebook(request: Request, user: OptionalCurrentUser):
    return templates.TemplateResponse(
        request=request, name="phonebook.j2.html", context={"user": user}
    )
