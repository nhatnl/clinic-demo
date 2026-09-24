from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.constants import Genders


class PatientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)

    age: int = Field(ge=0, le=150)

    gender: Genders = Field(default=Genders.NO_PROVIDED)


class PatientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=3, max_length=20)
    last_name: str | None = Field(default=None, min_length=3, max_length=20)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: Genders | None = Field(default=None)

    @field_validator("first_name", "last_name", "age", "gender", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Patient fields cannot be null")
        return value


class PatientSearchParams(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    age_from: int | None = Field(default=None, ge=0, le=150)
    age_to: int | None = Field(default=None, ge=0, le=150)
    gender: Genders | None = Field(default=None)

    @model_validator(mode="after")
    def validate_age_range(self):
        if (
            self.age_from is not None
            and self.age_to is not None
            and self.age_from > self.age_to
        ):
            raise ValueError("age_from must be less than or equal to age_to")
        return self
