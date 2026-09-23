from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.auth.schemas import AccessToken, SignIn
from src.auth.services import authenticated_user, generate_access_token
from src.config import settings
from src.database import get_session

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-in", response_model=AccessToken)
def sign_in(credentials: SignIn, session: SessionDep) -> AccessToken:
    user = authenticated_user(credentials, session)

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_DURATION)
    access_token = generate_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires,
    )
    return access_token
