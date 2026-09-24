from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from src.auth import exceptions as auth_exceptions
from src.auth.models import User
from src.consultations import exceptions
from src.consultations.models import Consultation
from src.consultations.schemas import ConsultationCreate
from src.diagnosis.model import Diagnosis
from src.patients.models import Patient


def create_consultation(
    data: ConsultationCreate,
    session: Session,
    current_user: dict,
) -> Consultation:
    creator = session.get(User, int(current_user["id"]))
    if creator is None:
        raise auth_exceptions.UserNotFound

    patient = session.get(Patient, data.patient_id)
    if patient is None:
        raise exceptions.PatientNotFound

    diagnoses = list(
        session.exec(
            select(Diagnosis).where(
                Diagnosis.code.in_(data.diagnosis_codes),
                Diagnosis.is_valid_for_submission.is_(True),
            )
        ).all()
    )
    if len(diagnoses) != len(data.diagnosis_codes):
        raise exceptions.DiagnosisNotFound

    consultation = Consultation(
        patient_id=data.patient_id,
        patient=patient,
        created_by_id=creator.id,
        created_by=creator,
        note=data.note,
        diagnoses=diagnoses,
    )
    session.add(consultation)
    session.commit()
    session.refresh(consultation)
    return consultation


def list_consultations(
    session: Session,
    patient_name: str | None = None,
    diagnosis_code: str | None = None,
    patient_id: int | None = None,
) -> list[Consultation]:
    statement = select(Consultation).options(
        selectinload(Consultation.patient),
        selectinload(Consultation.created_by),
        selectinload(Consultation.diagnoses),
    )

    if patient_name is not None:
        statement = statement.join(Patient).where(
            (Patient.first_name + " " + Patient.last_name).ilike(
                f"%{patient_name.strip()}%"
            )
        )

    if patient_id is not None:
        statement = statement.where(Consultation.patient_id == patient_id)

    if diagnosis_code is not None:
        statement = statement.join(Consultation.diagnoses).where(
            Diagnosis.code == diagnosis_code.strip().upper()
        )

    statement = statement.order_by(
        Consultation.created_at.desc(),
        Consultation.id.desc(),
    )
    return list(session.exec(statement).all())


def get_consultation(consultation_id: int, session: Session) -> Consultation:
    consultation = session.exec(
        select(Consultation)
        .where(Consultation.id == consultation_id)
        .options(
            selectinload(Consultation.patient),
            selectinload(Consultation.created_by),
            selectinload(Consultation.diagnoses),
        )
    ).first()
    if consultation is None:
        raise exceptions.ConsultationNotFound
    return consultation
