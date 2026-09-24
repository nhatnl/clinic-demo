from sqlmodel import Field, Relationship, SQLModel

from src.auth.models import User
from src.diagnosis.model import Diagnosis
from src.model import BaseModel
from src.patients.models import Patient


class ConsultationDiagnosis(SQLModel, table=True):
    __tablename__ = "consultation_diagnoses"

    consultation_id: int | None = Field(
        default=None,
        foreign_key="consultations.id",
        primary_key=True,
    )
    diagnosis_code: str | None = Field(
        default=None,
        foreign_key="diagnoses.code",
        primary_key=True,
        index=True,
        max_length=8,
    )


class Consultation(BaseModel, table=True):
    __tablename__ = "consultations"

    patient_id: int = Field(
        foreign_key="patients.id",
        nullable=False,
        index=True,
    )
    created_by_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )
    note: str = Field(nullable=False, min_length=1)

    patient: Patient = Relationship()
    created_by: User = Relationship()
    diagnoses: list[Diagnosis] = Relationship(link_model=ConsultationDiagnosis)
