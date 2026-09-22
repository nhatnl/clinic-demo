from fastapi import HTTPException, status

permission_denied = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Permission Denined"
)
