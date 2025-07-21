"""
pothos geo asset management core/db.py
Copyright (C) 2025  Ole Lange

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel, func, select

from app.core.config import settings

from app.models import *
from app.models.crud.user import create_user
from app.models.user import UserCreate, UserRole

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session, engine=engine) -> None:
    SQLModel.metadata.create_all(engine)

    # check if there are any users in the DB, if not create a root user with
    # configured default credentials
    num_users = session.exec(select(func.count("*")).select_from(User)).first()
    if num_users == 0:
        create_user(
            session,
            None,
            UserCreate(
                role=UserRole.ADMIN,
                username=settings.DEFAULT_ROOT_USER,
                password=settings.DEFAULT_ROOT_PASSWORD,
            ),
            created_by_system=True,
        )


def drop_db(engine=engine) -> None:
    SQLModel.metadata.drop_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
