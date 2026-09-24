from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.logs.exceptions import InvalidDataField


class ActivityLogCreate(BaseModel):
    event: str = Field(nullable=False, min_length=3, max_length=20)
    user_id: int = Field(gt=0)
    data: dict[str, Any] = Field(nullable=False, default_factory=dict)

    @field_validator("data")
    @classmethod
    def is_data_valid(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict) or not data:
            raise InvalidDataField
        return data
