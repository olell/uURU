from sqlmodel import Session, col, select
import uuid

from app.models.user import PasswordChange, User, UserCreate, UserRole, UserUpdate
from app.models.crud import CRUDNotAllowedException

from app.core.security import get_password_hash, verify_password


def create_user(
    session: Session,
    creating_user: User | None,
    new_user: UserCreate,
    created_by_system=False,
) -> User:

    if new_user.role != UserRole.USER and not created_by_system:
        if creating_user is None or creating_user.role != UserRole.ADMIN:
            raise CRUDNotAllowedException("You may not register an admin account")

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
    if "password" in data and data["password"] is not None:
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
    statement = select(User).where(User.id == uuid.UUID(user_id))
    user = session.exec(statement).first()

    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    return user


def filter_user_by_username(
    session: Session, username: str | None = None
) -> list[User]:
    query = select(User)
    if username is not None:
        query = query.where(col(User.username).contains(username))

    return list(session.exec(query).all())


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    db_user = get_user_by_username(session, username)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user


def change_password(session: Session, user: User, credentials: PasswordChange) -> User:
    if not verify_password(credentials.current_password, user.password_hash):
        raise CRUDNotAllowedException("Invalid current password")

    user.password_hash = get_password_hash(credentials.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
