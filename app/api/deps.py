from typing import Annotated
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.core.db import SessionDep
from app.core.security import JWT_ALGORITHM
from app.models.user import TokenPayload, User
from app.models.crud.user import get_user_by_id


def get_current_user(
    session: SessionDep,
    token: str = Depends(APIKeyHeader(name="x-auth-token")),
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
