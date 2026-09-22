from typing import Annotated

from fastapi import Depends

from src.admin.exceptions import permission_denied
from src.auth.constants import Roles
from src.auth.dependencies import get_current_user


def require_admin(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    if current_user["role"] != Roles.ADMIN:
        raise permission_denied from None

    return current_user
