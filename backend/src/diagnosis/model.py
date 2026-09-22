from sqlmodel import Field, SQLModel


class Diagnosis(SQLModel, table=True):
    __tablename__ = "diagnoses"

    code: str = Field(nullable=False, min_length=1, max_length=8, primary_key=True)
    name: str = Field(nullable=False, min_length=3, max_length=100)
    description: str = Field(nullable=True, max_length=500)
    is_valid_for_submission: bool = Field(default=False, nullable=False)

    parent_code: str | None = Field(nullable=True, default=None, foreign_key="diagnoses.code")
