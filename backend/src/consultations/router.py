from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from src.auth.dependencies import get_current_user
from src.consultations import services
from src.consultations.schemas import (
    ConsultationCreate,
    ConsultationQueryParams,
    ConsultationResponse,
)
from src.database import get_session

router = APIRouter(
    tags=["Consultations"],
    dependencies=[Depends(get_current_user)],
)
SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/consultation",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_consultation(
    data: ConsultationCreate,
    session: SessionDep,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    return services.create_consultation(data, session, current_user)


@router.get("/consultation", response_model=list[ConsultationResponse])
def list_consultations(
    session: SessionDep,
    params: Annotated[ConsultationQueryParams, Query()],
):
    patient_name = params.patient_name if params.patient_name is not None else params.patient
    return services.list_consultations(
        session, patient_name, params.diagnosis_code, params.patient_id
    )


@router.get("/consultation/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(consultation_id: int, session: SessionDep):
    return services.get_consultation(consultation_id, session)
