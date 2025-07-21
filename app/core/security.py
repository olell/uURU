from datetime import datetime, timedelta, timezone
from typing import Any
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
import random
import string

from app.core.config import settings

JWT_ALGORITHM = "HS256"
hasher = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    return hasher.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def generate_extension_password():
    return "".join(
        random.choice(settings.EXTENSION_PASSWORD_CHARS)
        for _ in range(settings.EXTENSION_PASSWORD_LENGTH)
    )


def generate_extension_token():
    return settings.EXTENSION_TOKEN_LENGTH + "".join(
        random.choice(string.digits) for _ in range(settings.EXTENSION_TOKEN_LENGTH)
    )
