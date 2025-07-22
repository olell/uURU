from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import settings
from app.core.db import SessionDep
from app.core.security import create_access_token
from app.models.crud.user import authenticate_user, create_user
from app.models.user import UserCreate
from app.web.deps import OptionalCurrentUser
from app.web.templates import templates

router = APIRouter(prefix="/user")


@router.get("/login", response_class=HTMLResponse | RedirectResponse)
def login_page(request: Request, current_user: OptionalCurrentUser):
    if current_user:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="login.j2.html")


@router.post(
    "/login", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def login_handle(
    session: SessionDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    current_user: OptionalCurrentUser,
):
    if current_user is not None:
        return "/"

    user = authenticate_user(session, username, password)
    if not user:
        # todo, pass an error message
        return "/user/login"

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires)

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("session", token)
    return response


@router.get(
    "/logout", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def logout(user: OptionalCurrentUser):
    if not user:
        return "/"

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session")
    return response


@router.post(
    "/register", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def register_handle(session: SessionDep, data: Annotated[UserCreate, Form()]):
    create_user(session, None, data)
    return "/user/login"
