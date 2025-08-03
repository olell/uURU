from typing import Annotated
from fastapi import APIRouter, Request, status, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.db import SessionAsteriskDep, SessionDep
from app.models.crud import CRUDNotAllowedException
from app.telephoning.main import Telephoning
from app.web.deps import CurrentUser
from app.web.message import MessageBroker
from app.web.templates import templates
from app.models.extension import ExtensionCreate, ExtensionUpdate
from app.models.crud.extension import (
    create_extension,
    delete_extension,
    get_extension_by_id,
    update_extension,
)

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
        request,
        "extension/create.j2.html",
        {"user": current_user},
    )


@router.post(
    "/create", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER
)
def create_extension_handle(
    request: Request,
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    data: Annotated[ExtensionCreate, Form()],
    user: CurrentUser,
):
    try:
        create_extension(session, session_asterisk, user, data)
    except Exception as e:
        if isinstance(e, CRUDNotAllowedException):
            MessageBroker.push(
                request,
                {
                    "message": f"Failed to create extension: {str(e)}",
                    "category": "error",
                },
            )
        else:
            MessageBroker.push(
                request, {"message": "Failed to create extension", "category": "error"}
            )
        return "/extension/create"
    MessageBroker.push(
        request, {"message": "Created extension!", "category": "success"}
    )
    return "/extension/own"


@router.get(
    "/delete/{extension}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
)
def delete_extension_handle(
    request: Request,
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    extension: str,
    user: CurrentUser,
):
    try:
        delete_extension(
            session,
            session_asterisk,
            user,
            get_extension_by_id(session, extension, False),
        )
    except Exception as e:
        MessageBroker.push(
            request, {"message": "Failed to delete extension!", "category": "error"}
        )
        return
    MessageBroker.push(
        request, {"message": "Deleted extension!", "category": "success"}
    )
    return "/extension/own"


@router.get("/edit/{extension}", response_class=HTMLResponse)
def edit_extension_page(
    request: Request, session: SessionDep, user: CurrentUser, extension: str
):
    extension = get_extension_by_id(session, extension, False)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )
    return templates.TemplateResponse(
        request, "extension/create.j2.html", context={"user": user, "edit": extension}
    )


@router.post(
    "/edit/{extension_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
)
def edit_extension_handle(
    request: Request,
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    extension_id: str,
    data: Annotated[ExtensionUpdate, Form()],
):
    extension = get_extension_by_id(session, extension_id, False)
    if extension is None:
        return f"/extension/edit/{extension_id}"
    try:
        update_extension(session, session_asterisk, user, extension, data)
    except:
        MessageBroker.push(
            request, {"message": "Failed to update extension!", "category": "error"}
        )
        return "/extension/own"
    MessageBroker.push(request, {"message": "Saved!", "category": "success"})
    return f"/extension/edit/{extension_id}"
