# from fastapi import HTTPException, status

# credentials_exception = HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Invalid authentication credentials",
#     headers={"WWW-Authenticate": "Bearer"},
# )

# user_existing_exception = HTTPException(
#     status_code=status.HTTP_400_BAD_REQUEST,
#     detail="Email already exist"
# )

from src.exceptions import Error


class UserNotFound(Error):
    pass


class IncorrectPassword(Error):
    pass


class InvalidJwtToken(Error):
    pass


class UserAlreadyExist(Error):
    pass


class ForbiddenError(Error):
    pass
