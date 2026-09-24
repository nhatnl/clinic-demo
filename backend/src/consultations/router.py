from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from src.consultations import services
from src.consultations.schemas import ConsultationCreate, ConsultationResponse
from src.database import get_session

router = APIRouter(tags=["Consultations"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/consultation",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_consultation(
    data: ConsultationCreate,
    session: SessionDep,
) -> ConsultationResponse:
    return services.create_consultation(data, session)


@router.get("/consultation", response_model=list[ConsultationResponse])
def list_consultations(
    session: SessionDep,
    patient: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    diagnosis_code: Annotated[
        str | None,
        Query(min_length=1, max_length=8),
    ] = None,
) -> list[ConsultationResponse]:
    return services.list_consultations(session, patient, diagnosis_code)
