from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.constants import JWT_ALGORITHM, Roles
from src.auth.exceptions import ForbiddenError, InvalidJwtToken
from src.config import settings

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError as exc:
        raise InvalidJwtToken from exc
    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise InvalidJwtToken

    return {
        "id": user_id,
        "role": role,
    }


def allowed_roles(allowed_roles: list[Roles]):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise ForbiddenError
        return user

    return role_checker
