from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlalchemy

from app.core.config import settings
from app.core.db import SessionDep
from app.core.security import create_access_token
from app.models.crud import CRUDNotAllowedException
from app.models.crud.user import authenticate_user, change_password, create_user
from app.models.user import PasswordChange, UserCreate
from app.web.deps import CurrentUser, OptionalCurrentUser
from app.web.message import MessageBroker
from app.web.templates import templates

router = APIRouter(prefix="/user")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user: OptionalCurrentUser):
    if current_user:
        MessageBroker.push(
            request, {"message": "You're already logged in!", "category": "warning"}
        )
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="user/login.j2.html")


@router.post(
    "/login", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def login_handle(
    request: Request,
    session: SessionDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    current_user: OptionalCurrentUser,
):
    if current_user is not None:
        MessageBroker.push(
            request, {"message": "You're already logged in!", "category": "warning"}
        )
        return "/"

    user = authenticate_user(session, username, password)
    if not user:
        MessageBroker.push(
            request,
            {
                "message": "Failed to log in! (Invalid username or password?)",
                "category": "error",
            },
        )
        return "/user/login"

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires)

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("auth", token)
    MessageBroker.push(request, {"message": f"Hello {user.username} 👋"})
    return response


@router.get(
    "/logout", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def logout(request: Request, user: OptionalCurrentUser):
    if not user:
        return "/"

    MessageBroker.push(request, {"message": "See ya!"})

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("auth")
    return response


@router.post(
    "/register", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def register_handle(
    request: Request, session: SessionDep, data: Annotated[UserCreate, Form()]
):
    try:
        create_user(session, None, data)
    except sqlalchemy.exc.IntegrityError:
        MessageBroker.push(
            request, {"message": f"Username already in use!", "category": "error"}
        )
    MessageBroker.push(
        request, {"message": "Account successfully created!", "category": "success"}
    )
    return "/user/login"


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, user: CurrentUser):
    return templates.TemplateResponse(request, "user/settings.j2.html", {"user": user})


@router.post(
    "/change_password",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
)
def settings_handle(
    request: Request,
    session: SessionDep,
    user: CurrentUser,
    credentials: Annotated[PasswordChange, Form()],
):
    try:
        change_password(session, user, credentials)
    except CRUDNotAllowedException as e:
        MessageBroker.push(request, {"message": str(e), "category": "error"})
    MessageBroker.push(request, {"message": "Password Changed!", "category": "success"})
    return "/user/settings"
