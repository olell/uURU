"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Literal, Optional

from fastapi import APIRouter, status, HTTPException
import sqlalchemy

from app.api.deps import OptionalCurrentUser, SessionDep, CurrentUser
from app.core.db import SessionAsteriskDep
from app.core.ldap import LDAPDep
from app.models.asterisk import PSContact
from app.models.crud import CRUDNotAllowedException
from app.models.crud.asterisk import (
    get_contact,
    get_extensions_with_contacts,
    has_contact,
)
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
from app.models.user import UserRole

router = APIRouter(prefix="/extension", tags=["extension"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ExtensionBase)
def create(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    ldap: LDAPDep,
    user: CurrentUser,
    data: ExtensionCreate,
):
    try:
        return create_extension(session, session_asterisk, ldap, user, data)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Extension already in use"
        )
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{extension}", response_model=ExtensionBase)
def update(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    ldap: LDAPDep,
    user: CurrentUser,
    extension: str,
    data: ExtensionUpdate,
):
    ext = get_extension_by_id(session, extension, public=False)

    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )

    try:
        return update_extension(session, session_asterisk, ldap, user, ext, data)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{extension}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    ldap: LDAPDep,
    user: CurrentUser,
    extension: str,
):
    ext = get_extension_by_id(session, extension, public=False)

    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )

    try:
        delete_extension(session, session_asterisk, ldap, user, ext)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/info/{extension}")
def get(session: SessionDep, user: CurrentUser, extension: str) -> Extension:
    ext = get_extension_by_id(session, extension, False)

    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found"
        )

    if user.role != UserRole.ADMIN and ext.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden!")

    return ext


@router.get("/own")
def get_own(session: SessionDep, user: CurrentUser):
    return user.extensions


@router.get("/phonebook", response_model=list[ExtensionBase])
def phonebook(
    *,
    session: SessionDep,
    user: OptionalCurrentUser = None,
    query: Optional[str] = None,
    public: bool = True,
):
    if not public and (user is None or user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may not request non-public extension",
        )

    return filter_extensions_by_name(session, user, query, public)


@router.get("/all")
def admin_phonebook(
    *,
    session: SessionDep,
    user: CurrentUser,
    query: Optional[str] = None,
    public: bool = False,
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may not request the all extensions!",
        )
    return phonebook(session=session, user=user, query=query, public=public)


@router.get("/online")
def get_extensions_online(
    *, session: SessionDep, session_asterisk: SessionAsteriskDep, user: CurrentUser
) -> list[ExtensionBase]:
    try:
        extensions = get_extensions_with_contacts(session, session_asterisk, user)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return extensions


@router.get("/is_online/{extension}")
def is_extension_online(
    *,
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    extension: str,
) -> dict[Literal["online"], bool]:
    extension = get_extension_by_id(session, extension, False)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found!"
        )
    try:
        state = has_contact(session_asterisk, extension, user)
        return {"online": state}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/contact/{extension}")
def get_extension_contact(
    *,
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    extension: str,
) -> PSContact | None:
    extension = get_extension_by_id(session, extension, False)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found!"
        )
    try:
        return get_contact(session_asterisk, extension, user)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
