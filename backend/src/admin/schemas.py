from pydantic import BaseModel, EmailStr, Field

from src.auth.constants import Roles


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    first_name: str | None
    last_name: str | None

class UserCreateAdmin(BaseModel):
    first_name: str | None = Field(default=None, max_length=20)
    last_name: str | None = Field(default=None, max_length=20)
    role: Roles
    email: EmailStr