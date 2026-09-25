from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlmodel import Session, select

from src.auth.constants import Roles
from src.auth.dependencies import allowed_roles
from src.database import get_session
from src.diagnosis.model import Diagnosis
from src.pagination import Page, Pagination, paginate

router = APIRouter(
    prefix="/diagnosis",
    tags=["Diagnosis"],
    dependencies=[Depends(allowed_roles([Roles.ADMIN, Roles.DOCTOR, Roles.NURSE]))],
)
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=Page[Diagnosis])
def get_diagnosis(
    session: SessionDep,
    search: Annotated[str, Query(min_length=1, max_length=100)],
    pagination: Annotated[Pagination, Depends()],
) -> Page[Diagnosis]:
    term = search.strip()
    if not term:
        return Page(items=[], total=0, **pagination.model_dump())
    return paginate(
        session,
        select(Diagnosis)
        .where(or_(Diagnosis.code.ilike(f"%{term}%"), Diagnosis.name.ilike(f"%{term}%")))
        .order_by(Diagnosis.code),
        pagination,
    )
