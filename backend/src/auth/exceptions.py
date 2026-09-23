from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

user_existing_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already exist"
)