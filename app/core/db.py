from logging import getLogger
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel, func, select

from app.core.config import settings

from app.models import *
from app.models.user import User
from app.models.crud.user import create_user
from app.models.user import UserCreate, UserRole

logger = getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
engine_asterisk = create_engine(str(settings.SQLACLCHEMY_ASTERISK_DATABASE_URI))


def init_db(session, engine=engine) -> None:
    SQLModel.metadata.create_all(engine, tables=[x.__table__ for x in tables])
    SQLModel.metadata.create_all(
        engine_asterisk, tables=[x.__table__ for x in asterisk_tables]
    )
    logger.info(f"Created tables")

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
        logger.info(f"Created initial user ({settings.DEFAULT_ROOT_USER})")


def drop_db(engine=engine) -> None:
    SQLModel.metadata.drop_all(engine, [x.__table__ for x in tables])
    logger.info(f"Dropped all @ ({engine})")


def get_session():
    with Session(engine) as session:
        yield session


def get_asterisk_session():
    with Session(engine_asterisk) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
SessionAsteriskDep = Annotated[Session, Depends(get_asterisk_session)]
