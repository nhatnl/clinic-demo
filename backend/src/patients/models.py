from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlmodel import Field

from src.constants import Genders
from src.model import BaseModel


class Patient(BaseModel, table=True):
    __tablename__ = "patients"

    first_name: str = Field(nullable=False, min_length=3, max_length=20)
    last_name: str = Field(nullable=False, min_length=3, max_length=20)
    age: int = Field(nullable=False, ge=0, le=150)

    gender: Genders = Field(
        sa_column=Column(
            SqlEnum(Genders, name="genders", native_enum=True),
            default=Genders.NO_PROVIDED,
        )
    )

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
