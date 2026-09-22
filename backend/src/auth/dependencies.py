from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.exceptions import credentials_exception
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        raise credentials_exception from None

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise credentials_exception

    return {
        "id": user_id,
        "role": role,
    }
