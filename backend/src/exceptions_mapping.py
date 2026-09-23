from fastapi import status

from src.auth import exceptions as auth_exceptions

HTTP_ERROR_MAP = {
    auth_exceptions.UserNotFound: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
    auth_exceptions.IncorrectPassword: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
    auth_exceptions.InvalidJwtToken: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
    auth_exceptions.UserAlreadyExist: (
        status.HTTP_400_BAD_REQUEST,
        "User already exists",
        None,
    ),
}
