from datetime import datetime, timezone
from sqlmodel import Field, Session, SQLModel


class BaseModel(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False) 
