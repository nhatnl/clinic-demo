from pwdlib import PasswordHash
from sqlmodel import Session, select

from src.auth import exceptions
from src.auth.constants import Roles
from src.auth.models import User
from src.auth.schemas import UserCreate

password_hash = PasswordHash.recommended()

def create_user(data: UserCreate, session: Session) -> User:
    existing_user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing_user:
        raise exceptions.user_existing_exception

    user = User(
        email=data.email,
        password_hash=password_hash.hash(data.password),
        role=Roles.USER
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
