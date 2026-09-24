from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlmodel import Session, select

from src.database import get_session
from src.diagnosis.model import Diagnosis

router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[Diagnosis])
def get_diagnosis(
    session: SessionDep,
    search: Annotated[str, Query(min_length=1, max_length=100)],
) -> list[Diagnosis]:
    term = search.strip()
    if not term:
        return []
    return list(
        session.exec(
            select(Diagnosis)
            .where(or_(Diagnosis.code.ilike(f"%{term}%"), Diagnosis.name.ilike(f"%{term}%")))
            .order_by(Diagnosis.code)
            .limit(100)
        ).all()
    )
