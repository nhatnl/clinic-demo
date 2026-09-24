from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from src.consultations import exceptions
from src.consultations.models import Consultation
from src.consultations.schemas import ConsultationCreate
from src.diagnosis.model import Diagnosis
from src.patients.models import Patient


def create_consultation(data: ConsultationCreate, session: Session) -> Consultation:
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
        note=data.note,
        diagnoses=diagnoses,
    )
    session.add(consultation)
    session.commit()
    session.refresh(consultation)
    return consultation


def list_consultations(
    session: Session,
    patient: str | None = None,
    diagnosis_code: str | None = None,
) -> list[Consultation]:
    statement = select(Consultation).options(
        selectinload(Consultation.patient),
        selectinload(Consultation.diagnoses),
    )

    if patient is not None:
        statement = statement.join(Patient).where(
            Patient.name.ilike(f"%{patient.strip()}%")
        )

    if diagnosis_code is not None:
        statement = statement.join(Consultation.diagnoses).where(
            Diagnosis.code == diagnosis_code.strip().upper()
        )

    statement = statement.order_by(
        Consultation.created_at.desc(),
        Consultation.id.desc(),
    )
    return list(session.exec(statement).all())
