"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from collections.abc import Generator
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.db import get_session, init_db, drop_db
from app.main import app as fastapi_app
from app.tests.util.user import user_authentication_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:

    engine = create_engine(str(settings.SQLALCHEMY_TEST_DATABASE_URI))

    def get_session_override():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = get_session_override
    print("Using test database @", engine.url)

    with Session(engine) as session:
        init_db(session, engine=engine)
        yield session

    fastapi_app.dependency_overrides.pop(get_session, None)
    drop_db(engine=engine)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture(scope="module")
def root_token_headers(client: TestClient) -> dict[str, str]:
    return user_authentication_headers(
        client, settings.DEFAULT_ROOT_USER, settings.DEFAULT_ROOT_PASSWORD
    )
