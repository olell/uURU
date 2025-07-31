from typing import Optional
from sqlmodel import Session, select, col, or_
import sqlalchemy

from pydantic_extra_types.mac_address import MacAddress

from app.core.security import generate_extension_password, generate_extension_token

from app.models.crud import CRUDNotAllowedException
from app.models.crud.asterisk import (
    create_asterisk_extension,
    delete_asterisk_extension,
)
from app.models.user import User, UserRole
from app.models.extension import (
    ExtensionCreate,
    Extension,
    ExtensionUpdate,
    TemporaryExtensions,
)
from app.core.config import settings
from app.telephoning.main import Telephoning


def create_extension(
    session: Session, session_asterisk: Session, user: User, extension: ExtensionCreate
) -> Extension:

    flavor = Telephoning.get_flavor_by_type(extension.type)
    if flavor is None:
        raise CRUDNotAllowedException("Unknown phone type!")

    if user.role != UserRole.ADMIN:  # check that the extension is not reserved
        ext = int(extension.extension)
        for rule in settings.RESERVED_EXTENSIONS:
            if (isinstance(rule, int) and ext == rule) or (
                isinstance(rule, tuple) and ext >= rule[0] and ext <= rule[1]
            ):
                raise CRUDNotAllowedException("This extension is reserved!")

        if not flavor.is_public():
            raise CRUDNotAllowedException(
                "Normal users may not create this kind of extension!"
            )

    try:
        db_obj = Extension.model_validate(
            extension,
            update={
                "password": generate_extension_password(),
                "token": generate_extension_token(),
                "user_id": user.id,
            },
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
    except sqlalchemy.exc.IntegrityError:
        raise CRUDNotAllowedException("Extension not available")

    create_asterisk_extension(
        session_asterisk,
        extension=db_obj.extension,
        password=db_obj.password,
        type=db_obj.type,
    )
    flavor.on_extension_create(session, session_asterisk, db_obj)

    return db_obj


def update_extension(
    session: Session,
    session_asterisk: Session,
    user: User,
    extension: Extension,
    update_data: ExtensionUpdate,
) -> Extension:

    if not (extension.user_id == user.id or user.role == UserRole.ADMIN):
        raise CRUDNotAllowedException("You're not allowed to edit this extension")

    flavor = Telephoning.get_flavor_by_type(extension.type)
    if flavor is None:
        raise CRUDNotAllowedException("Unkown phone type!")

    data = update_data.model_dump(exclude_unset=True)
    extension.sqlmodel_update(data)
    session.add(extension)
    session.commit()
    session.refresh(extension)

    flavor.on_extension_update(session, session_asterisk, extension)

    return extension


def delete_extension(
    session: Session, session_asterisk: Session, user: User, extension: Extension
) -> None:
    if not (extension.user_id == user.id or user.role == UserRole.ADMIN):
        raise CRUDNotAllowedException("You're not allowed to delete this extension")

    flavor = Telephoning.get_flavor_by_type(extension.type)
    if flavor is None:
        raise CRUDNotAllowedException("Unkown phone type!")

    flavor.on_extension_delete(session, session_asterisk, extension)
    delete_asterisk_extension(session_asterisk, extension)

    session.delete(extension)
    session.commit()
    session.refresh(user)  # todo: is this required to update the list of extensions?


def delete_tmp_extension(
    session: Session, session_asterisk: Session, tmp_extension: TemporaryExtensions
) -> None:
    delete_asterisk_extension(session_asterisk, tmp_extension)
    session.delete(tmp_extension)
    session.commit()


def get_extension_by_id(
    session: Session, extension_id: str, public=True
) -> Extension | None:
    query = select(Extension).where(Extension.extension == extension_id)

    if public:
        query = query.where(Extension.public == True)

    return session.exec(query).first()


def get_extension_by_extra_field(
    session: Session, key: str, value: any
) -> Extension | None:
    # TODO: This should be optimized!
    all_extensions = session.exec(select(Extension)).all()
    for extension in all_extensions:
        if extension.extra_fields.get(key, None) == value:
            return extension
    return None


def get_extension_by_token(session: Session, token: str) -> Extension | None:
    return session.exec(select(Extension).where(Extension.token == token)).first()


def get_tmp_extension_by_id(
    session: Session, extension_id: str
) -> TemporaryExtensions | None:
    return session.exec(
        select(TemporaryExtensions).where(TemporaryExtensions.extension == extension_id)
    ).first()


def filter_extensions_by_name(
    session: Session,
    user: Optional[User] = None,
    name: Optional[str] = None,
    public=True,
    order=True,
) -> list[Extension]:
    query = select(Extension)

    if name is not None:  # filter by name
        query = query.where(col(Extension.name).contains(name))
    if public and user is None:  # filter for public only
        query = query.where(Extension.public == True)
    elif public and user is not None:  # filter for public only + users own
        query = query.where(or_(Extension.public == True, Extension.user_id == user.id))
    if order:  # order by extension number
        query = query.order_by(Extension.extension)

    return list(session.exec(query).all())
