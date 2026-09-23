import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.auth.constants import Roles


class SignIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")

        if re.search(r"\s", password):
            raise ValueError("Password must not contain whitespace")

        return password


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str | None = Field(default=None, min_length=1, max_length=20)
    last_name: str | None = Field(default=None, min_length=1, max_length=20)
    role: Roles

    password: str = Field(min_length=1, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")

        if re.search(r"\s", password):
            raise ValueError("Password must not contain whitespace")

        return password


class AccessToken(BaseModel):
    access_token: str
    expired_at: str


class TokenData(BaseModel):
    email: str
