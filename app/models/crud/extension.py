from sqlmodel import Session, select, col

from app.core.security import generate_extension_password

from app.models.crud import CRUDNotAllowedException
from app.models.user import User, UserRole
from app.models.extension import ExtensionCreate, Extension, ExtensionUpdate


def create_extension(
    session: Session, user: User, extension: ExtensionCreate
) -> Extension:

    db_obj = Extension.model_validate(
        extension,
        update={
            "password": generate_extension_password(),
            "token": "",
            "user_id": user.id,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return session


def update_extension(
    session: Session, user: User, extension: Extension, update_data: ExtensionUpdate
) -> Extension:

    if not (extension.user_id == user.id or user.role == UserRole.ADMIN):
        raise CRUDNotAllowedException("You're not allowed to edit this extension")

    data = update_data.model_dump(exclude_unset=True)
    extension.sqlmodel_update(data)
    session.add(extension)
    session.commit()
    session.refresh(extension)

    return extension


def delete_extension(session: Session, user: User, extension: Extension) -> None:
    if not (extension.user_id == user.id or user.role == UserRole.ADMIN):
        raise CRUDNotAllowedException("You're not allowed to delete this extension")

    session.delete(extension)
    session.commit()
    session.refresh(user)  # todo: is this required to update the list of extensions?


def get_extension_by_id(
    session: Session, extension_id: str, public=True
) -> Extension | None:
    query = select(Extension).where(Extension.extension == extension_id)

    if public:
        query = query.where(Extension.public == True)

    return session.exec(query).first()


def filter_extensions_by_name(
    session: Session, name: str, public=True, order=True
) -> list[Extension]:
    query = select(Extension).where(col(Extension.name).contains(name))

    if public:
        query = query.where(Extension.public == True)
    if order:
        query = query.order_by(Extension.extension)

    return list(session.exec(query).all())
