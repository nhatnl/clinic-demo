from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from src.auth.constants import Roles
from src.auth.dependencies import allowed_roles
from src.database import get_session
from src.patients import services
from src.patients.dependencies import valid_patient_id
from src.patients.models import Patient
from src.patients.schemas import PatientCreate, PatientSearchParams, PatientUpdate
from src.pagination import Page, Pagination

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    dependencies=[Depends(allowed_roles([Roles.ADMIN, Roles.DOCTOR, Roles.NURSE]))],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=Page[Patient])
def search_patients(
    params: Annotated[PatientSearchParams, Query()],
    session: SessionDep,
    pagination: Annotated[Pagination, Depends()],
):
    """Search patients."""
    return services.search_patients(params, session, pagination)


@router.post(
    "/",
    response_model=Patient,
    status_code=201,
    dependencies=[Depends(allowed_roles([Roles.ADMIN, Roles.DOCTOR, Roles.NURSE]))],
)
def create_patient(
    patient: PatientCreate,
    session: SessionDep,
    current_user: Annotated[
        dict, Depends(allowed_roles([Roles.ADMIN, Roles.DOCTOR, Roles.NURSE]))
    ],
):
    """Create a new patient."""
    return services.create_patient(patient, session, current_user)


@router.get("/{patient_id}", response_model=Patient)
def get_patient_by_id(
    patient_id: int,
    patient: Annotated[Patient, Depends(valid_patient_id)],
):
    """Get a patient by ID."""
    return patient


@router.put("/{patient_id}", response_model=Patient)
def update_patient(
    patient_id: int,
    patient: PatientUpdate,
    existing_patient: Annotated[Patient, Depends(valid_patient_id)],
    session: SessionDep,
    current_user: Annotated[
        dict, Depends(allowed_roles([Roles.ADMIN, Roles.DOCTOR, Roles.NURSE]))
    ],
):
    """Update a patient by ID."""
    return services.update_patient(patient, session, current_user, existing_patient)
