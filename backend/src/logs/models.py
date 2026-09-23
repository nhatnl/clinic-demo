from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from src.model import BaseModel


class ActivitiesLog(BaseModel, table=True):
    __tablename__ = "activities_logs"

    event: str = Field(nullable=False, max_length=50)
    data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False)
        )
    user_id: int = Field(nullable=False, foreign_key="users.id")