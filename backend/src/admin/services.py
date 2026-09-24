from pwdlib import PasswordHash
from sqlmodel import Session, select

from src.auth import exceptions
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.logs.schemas import ActivityLogCreate
from src.logs.services import create_activity_log

password_hash = PasswordHash.recommended()


def admin_create_user(data: UserCreate, session: Session, admin_id: int) -> User:
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
    session.flush()

    log = ActivityLogCreate(
        event="Admin Add User",
        user_id=admin_id,
        data={"created_user_id": user.id, "email": user.email},
    )
    create_activity_log(log, session)

    session.refresh(user)
    return user
