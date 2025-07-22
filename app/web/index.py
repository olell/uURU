from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.web.templates import templates

router = APIRouter()


@router.get("/", response_class=RedirectResponse)
def index():
    return "/phonebook"


@router.get("/phonebook", response_class=HTMLResponse)
def phonebook(request: Request):
    return templates.TemplateResponse(request=request, name="phonebook.j2.html")
