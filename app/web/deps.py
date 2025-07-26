from typing import Annotated
from fastapi import HTTPException, Depends, status, Header
from fastapi.security import APIKeyCookie
import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.core.db import SessionDep
from app.core.security import JWT_ALGORITHM
from app.models.user import TokenPayload, User, UserRole
from app.models.crud.user import get_user_by_id


def get_current_user_optional(
    session: SessionDep,
    token: str = Depends(APIKeyCookie(name="auth", auto_error=False)),
) -> User | None:
    if token is None:
        return None

    try:
        return get_current_user(session, token)
    except:
        return None


def get_current_user(
    session: SessionDep,
    token: str = Depends(APIKeyCookie(name="auth")),
) -> User:

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = get_user_by_id(session, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user



CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(get_current_user_optional)]

def get_current_admin_user(session: SessionDep, current_user: CurrentUser):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not permitted to visit this page"
        )
    return current_user

AdminUser = Annotated[User, Depends(get_current_admin_user)]