from sqlmodel import Session

from app.core.security import generate_extension_password

from app.models.user import User
from app.models.extension import ExtensionCreate, Extension


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
