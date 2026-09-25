from sqlmodel import Session, select

from src.logs.schemas import ActivityLogCreate
from src.logs.services import create_activity_log
from src.pagination import Pagination, paginate
from src.patients.models import Patient
from src.patients.schemas import PatientCreate, PatientSearchParams, PatientUpdate


def search_patients(params: PatientSearchParams, session: Session, pagination: Pagination):
    """Get patients."""
    statement = select(Patient)
    if params.name:
        statement = statement.where(
            (Patient.first_name + " " + Patient.last_name).ilike(
                f"%{params.name.strip()}%"
            )
        )
    if params.age_from is not None:
        statement = statement.where(Patient.age >= params.age_from)
    if params.age_to is not None:
        statement = statement.where(Patient.age <= params.age_to)
    if params.gender is not None:
        statement = statement.where(Patient.gender == params.gender)
    return paginate(session, statement.order_by(Patient.id), pagination)


def create_patient(patient_data: PatientCreate, session: Session, current_user: dict):
    """Create a new patient."""
    patient = Patient.model_validate(patient_data.model_dump())
    session.add(patient)

    session.flush()
    log = ActivityLogCreate(
        event="Patient Created",
        user_id=current_user["id"],
        data={
            "patient_data": {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": patient.age,
                "gender": patient.gender.value,
            }
        },
    )
    create_activity_log(log, session)

    session.refresh(patient)

    return patient


def get_patient_by_id(patient_id: int, session: Session):
    """Get a patient by ID."""
    return session.get(Patient, patient_id)


def update_patient(
    patient: PatientUpdate,
    session: Session,
    current_user: dict,
    existing_patient: Patient,
):
    """Update a patient."""

    log = ActivityLogCreate(
        event="Patient Updated",
        user_id=current_user["id"],
        data={
            "old_patient_data": {
                "first_name": existing_patient.first_name,
                "last_name": existing_patient.last_name,
                "age": existing_patient.age,
                "gender": existing_patient.gender.value,
            },
            "new_patient_data": {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": patient.age,
                "gender": patient.gender.value if patient.gender else None,
            },
        },
    )

    for key, value in patient.model_dump(exclude_unset=True).items():
        setattr(existing_patient, key, value)

    session.add(existing_patient)
    session.flush()

    create_activity_log(log, session)

    session.refresh(existing_patient)

    return existing_patient
