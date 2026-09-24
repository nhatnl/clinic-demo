from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.database import get_session
from src.patients import exceptions, services
from src.patients.models import Patient


def valid_patient_id(
    patient_id: int, session: Annotated[Session, Depends(get_session)]
) -> Patient:
    patient = services.get_patient_by_id(patient_id, session)
    if not patient:
        raise exceptions.PatientNotFound
    return patient
