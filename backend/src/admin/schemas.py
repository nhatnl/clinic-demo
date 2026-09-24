from pydantic import BaseModel, EmailStr, Field

from src.auth.constants import Roles


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: Roles
    first_name: str | None
    last_name: str | None


class UserCreateAdmin(BaseModel):
    first_name: str | None = Field(default=None, max_length=20)
    last_name: str | None = Field(default=None, max_length=20)
    role: Roles
    email: EmailStr
