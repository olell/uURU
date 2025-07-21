from typing import Annotated
import uuid
from fastapi import APIRouter, Body, HTTPException
from datetime import timedelta
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser
from app.core.db import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.models.crud.user import authenticate_user, get_user_by_id
from app.models.user import Token, UserPublic

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
    return Token(token=token)


@router.get("/", response_model=UserPublic)
def info(*, user_id: uuid.UUID | None = None, session: SessionDep, user: CurrentUser):
    if user_id is None:
        return user
    else:
        return get_user_by_id(session, user_id, user)
