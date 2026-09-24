from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from src.auth.constants import Roles

DiagnosisCode = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=8),
]
ConsultationNote = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1)
]


class ConsultationCreate(BaseModel):
    patient_id: int = Field(gt=0)
    note: ConsultationNote
    diagnosis_codes: list[DiagnosisCode] = Field(min_length=1)

    @field_validator("diagnosis_codes")
    @classmethod
    def diagnosis_codes_must_be_unique(cls, codes: list[str]) -> list[str]:
        if len(codes) != len(set(codes)):
            raise ValueError("Diagnosis codes must be unique")
        return codes


class ConsultationQueryParams(BaseModel):
    patient: str | None = Field(default=None, min_length=1, max_length=50)
    patient_name: str | None = Field(default=None, min_length=1, max_length=50)
    patient_id: int | None = Field(default=None, gt=0)
    diagnosis_code: str | None = Field(default=None, min_length=1, max_length=8)


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int


class DiagnosisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str | None


class ConsultationCreatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    role: Roles


class ConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient: PatientResponse
    created_by: ConsultationCreatorResponse
    note: str
    diagnoses: list[DiagnosisResponse]
    created_at: datetime
    updated_at: datetime
