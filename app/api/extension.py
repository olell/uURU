from typing import Optional

from fastapi import APIRouter, status, HTTPException
import sqlalchemy

from app.api.deps import OptionalCurrentUser, SessionDep, CurrentUser
from app.core.db import SessionAsteriskDep
from app.models.crud import CRUDNotAllowedException
from app.models.extension import (
    Extension,
    ExtensionCreate,
    ExtensionBase,
    ExtensionUpdate,
)
from app.models.crud.extension import (
    create_extension,
    get_extension_by_id,
    update_extension,
    delete_extension,
    filter_extensions_by_name,
)

router = APIRouter(prefix="/extension", tags=["extension"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExtensionBase)
def create(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    data: ExtensionCreate,
):
    try:
        return create_extension(session, session_asterisk, user, data)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Extension already in use"
        )


@router.patch("/{extension}", response_model=ExtensionBase)
def update(
    session: SessionDep, user: CurrentUser, extension: str, data: ExtensionUpdate
):
    ext = get_extension_by_id(session, extension, public=False)

    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )

    try:
        return update_extension(session, user, ext, data)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{extension}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    extension: str,
):
    ext = get_extension_by_id(session, session_asterisk, extension, public=False)

    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )

    try:
        delete_extension(session, user, ext)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/own", response_model=list[Extension])
def get_own(session: SessionDep, user: CurrentUser):
    return user.extensions


@router.get("/phonebook", response_model=list[ExtensionBase])
def phonebook(
    *,
    session: SessionDep,
    user: OptionalCurrentUser = None,
    query: Optional[str] = None,
):
    return filter_extensions_by_name(session, user, query)
