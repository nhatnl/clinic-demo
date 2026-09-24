from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from sqlmodel import Session, select

from src.auth import exceptions
from src.auth.constants import JWT_ALGORITHM, Roles
from src.auth.models import User
from src.auth.schemas import AccessToken, SignIn, UserCreate
from src.config import settings

password_hash = PasswordHash.recommended()


def create_user(data: UserCreate, session: Session) -> User:
    existing_user = session.exec(select(User).where(User.email == data.email)).first()

    if existing_user:
        raise exceptions.UserAlreadyExist

    user = User(
        email=data.email,
        password_hash=password_hash.hash(data.password),
        role=Roles.USER,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticated_user(credential: SignIn, session) -> User:
    existing_user: User | None = session.exec(
        select(User).where(User.email == credential.email)
    ).first()
    if not existing_user:
        raise exceptions.UserNotFound

    if not password_hash.verify(credential.password, existing_user.password_hash):
        raise exceptions.IncorrectPassword

    return existing_user


def generate_access_token(data: dict, expires_delta: timedelta | None) -> AccessToken:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_DURATION
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)
    return AccessToken(access_token=encoded_jwt, expired_at=expire.isoformat())
