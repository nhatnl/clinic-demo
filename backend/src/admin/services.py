from pwdlib import PasswordHash
from sqlmodel import Session, select

from src.admin.schemas import UserCreateAdmin
from src.auth import exceptions
from src.auth.models import User
from src.logs.schemas import ActivityLogCreate
from src.logs.services import create_activity_log

password_hash = PasswordHash.recommended()


def admin_create_user(data: UserCreateAdmin, session: Session) -> User:
    existing_user = session.exec(select(User).where(User.email == data.email)).first()

    if existing_user:
        raise exceptions.UserAlreadyExist

    user = User(
        email=data.email,
        password_hash=password_hash.hash(data.password),
        role=data.role,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    log = ActivityLogCreate(event="Admin Add User", data={"user_data": user})
    create_activity_log(log, session)

    return user
