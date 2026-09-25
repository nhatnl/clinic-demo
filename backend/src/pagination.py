from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import Session, select

T = TypeVar("T")


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


def paginate(session: Session, statement, pagination: Pagination) -> Page:
    total = session.exec(
        select(func.count()).select_from(statement.order_by(None).subquery())
    ).one()
    items = list(
        session.exec(
            statement.offset((pagination.page - 1) * pagination.page_size).limit(
                pagination.page_size
            )
        ).all()
    )
    return Page(items=items, total=total, **pagination.model_dump())
