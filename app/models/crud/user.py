from sqlmodel import Session, select
import uuid

from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.models.crud import CRUDNotAllowedException

from app.core.security import get_password_hash, verify_password


def create_user(
    session: Session, creating_user: User | None, new_user: UserCreate
) -> User:

    if creating_user is not None and not creating_user.role == UserRole.ADMIN:
        raise CRUDNotAllowedException("Only admins are permitted to create new users")

    db_obj = User.model_validate(
        new_user, update={"password_hash": get_password_hash(new_user.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def update_user(
    session: Session, executing_user: User, target_user: User, update_data: UserUpdate
) -> User:

    if executing_user.id != target_user.id and executing_user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("You're not allowed to update this user")

    data = update_data.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in data:
        password = data["password"]
        hashed = get_password_hash(password)
        extra_data.update({"password_hash": hashed})
    target_user.sqlmodel_update(data, update=extra_data)

    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    return target_user


def delete_user(session: Session, executing_user: User, user_to_delete: User) -> None:
    if executing_user.id != user_to_delete.id and executing_user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("You're not allowed to delete this user")

    session.delete(user_to_delete)
    session.commit()


def get_user_by_id(session: Session, user_id: uuid.UUID) -> User | None:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    return user


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    db_user = get_user_by_username(session, username)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user
