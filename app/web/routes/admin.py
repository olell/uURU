from logging import getLogger
from typing import Annotated, Optional
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid

from app.core.db import SessionDep
from app.models.crud import CRUDNotAllowedException
from app.models.crud.extension import filter_extensions_by_name
from app.models.crud.user import filter_user_by_username, get_user_by_id, update_user
from app.models.user import UserRole, UserUpdate
from app.web.message import MessageBroker
from app.web.templates import templates
from app.web.deps import AdminUser

router = APIRouter(prefix="/admin")
logger = getLogger(__name__)


@router.get("/users", response_class=HTMLResponse)
def user_list_page(
    request: Request, session: SessionDep, user: AdminUser, query: Optional[str] = None
):
    users = filter_user_by_username(session, query)
    return templates.TemplateResponse(
        request, "admin/userlist.j2.html", {"user": user, "users": users}
    )


@router.get("/edit_user/{user_id}", response_class=HTMLResponse)
def user_edit(request: Request, session: SessionDep, admin: AdminUser, user_id: str):
    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    return templates.TemplateResponse(
        request,
        "admin/useredit.j2.html",
        {"user": admin, "edit": user, "UserRole": UserRole},
    )


@router.post(
    "/edit_user/{user_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
)
def user_edit_handle(
    request: Request,
    session: SessionDep,
    admin: AdminUser,
    user_id: str,
    data: Annotated[UserUpdate, Form()],
):
    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    if data.password.strip() == "":
        data.password = None
    if data.username.strip() == "":
        data.username = None
    if data.role.strip() == "":
        data.role = None

    try:
        update_user(session, admin, user, data)
        MessageBroker.push(
            request,
            {"message": f"Updated user!", "category": "success"},
        )
    except CRUDNotAllowedException as e:
        MessageBroker.push(
            request,
            {"message": f"Failed to update user: {str(e)}", "category": "error"},
        )
    except Exception as e:
        MessageBroker.push(
            request, {"message": "Couldn't update user", "category": "error"}
        )
    finally:
        return f"/admin/edit_user/{user_id}"


@router.get("/extensions", response_class=HTMLResponse)
def extensionlist(request: Request, session: SessionDep, user: AdminUser):
    extensions = filter_extensions_by_name(session, user, None, False)

    return templates.TemplateResponse(
        request, "admin/extensionlist.j2.html", {"user": user, "extensions": extensions}
    )
