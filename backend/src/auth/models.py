from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlmodel import Field

from src.auth.constants import Roles, UserStatus
from src.model import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"

    first_name: str | None = Field(default=None, nullable=True, max_length=20)
    last_name: str | None = Field(default=None, nullable=True, max_length=20)
    email: str = Field(nullable=False, max_length=50)
    status: UserStatus = Field(
        sa_column=Column(SqlEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    )

    role: Roles = Field(sa_column=Column(SqlEnum(Roles), nullable=False))
    password_hash: str = Field(nullable=False)
