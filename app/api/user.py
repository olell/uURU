"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import sqlalchemy
from sqlmodel import select, delete as sql_delete

from app.api.deps import CurrentUser, OptionalCurrentUser
from app.core.db import SessionDep
from app.core.config import settings
from app.core.security import create_access_token, generate_invite_code
from app.models.crud import CRUDNotAllowedException
from app.models.crud.user import (
    authenticate_user,
    create_user,
    delete_user,
    filter_user_by_username,
    get_user_by_id,
    update_user,
)
from app.models.crud.user import change_password as crud_change_password
from app.models.user import (
    Invite,
    InviteCreate,
    InviteVariant,
    PasswordChange,
    Token,
    UserPublic,
    UserCreate,
    UserRole,
    UserUpdate,
)

router = APIRouter(prefix="/user", tags=["user"])


class Credentials(BaseModel):
    username: str
    password: str = Field(min_length=10, max_length=100)


@router.post("/login")
def login(session: SessionDep, credentials: Annotated[Credentials, Body()]) -> Token:
    user = authenticate_user(session, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires)
    response = JSONResponse({"detail": "OK"})
    response.set_cookie(
        "auth",
        token,
        httponly=True,
    )
    return response


@router.get("/logout")
def logout():
    response = JSONResponse({"detail": "Bye!"})
    response.delete_cookie(key="auth", httponly=True)
    return response


@router.get("/", response_model=UserPublic)
def info(*, user_id: str | None = None, session: SessionDep, user: CurrentUser):
    if user_id is None:
        return user
    else:
        return get_user_by_id(session, user_id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(*, user_id: str | None = None, session: SessionDep, user: CurrentUser):
    try:
        if user_id is None:
            delete_user(session, user, user)
        else:
            delete_user(session, user, get_user_by_id(session, user_id))
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/")
def update(
    *,
    user_id: str | None = None,
    session: SessionDep,
    user: CurrentUser,
    data: UserUpdate,
):
    try:
        if user_id is None:
            update_user(session, user, user, data)
        else:
            update_user(session, user, get_user_by_id(session, user_id), data)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(
    *, session: SessionDep, executing: OptionalCurrentUser = None, new: UserCreate
):
    try:
        user = create_user(session, executing, new)
    except CRUDNotAllowedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You're not allowed to create this user ({str(e)})",
        )
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already in use"
        )

    return user


@router.patch("/password")
def change_password(*, session: SessionDep, user: CurrentUser, data: PasswordChange):
    try:
        crud_change_password(session, user, data)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return {"detail": "OK"}


@router.get("/all")
def all_users(*, session: SessionDep, user: CurrentUser) -> list[UserPublic]:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only!")

    users = filter_user_by_username(session)
    return users


@router.post("/invite")
def create_invite(
    *, session: SessionDep, user: CurrentUser, data: InviteCreate
) -> Invite:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only!")

    code = generate_invite_code()
    invite = Invite(
        invite=code,
        variant=data.variant,
        use_count=None if data.variant == InviteVariant.TIME else 0,
        max_uses=data.max_uses,
        valid_until=(
            None
            if data.variant == InviteVariant.COUNT
            else datetime.now()
            + timedelta(days=data.valid_days, hours=data.valid_hours)
        ),
    )
    session.add(invite)
    session.commit()

    return invite


@router.delete("/invite", status_code=status.HTTP_204_NO_CONTENT)
def delete_invite(*, session: SessionDep, user: CurrentUser, invite: str):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only!")

    session.exec(sql_delete(Invite).where(Invite.invite == invite))
    session.commit()
    return {}


@router.get("/invite")
def get_invites(*, session: SessionDep, user: CurrentUser) -> list[Invite]:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only!")

    invites = session.exec(select(Invite)).all()
    return list(invites)
