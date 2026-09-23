from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.admin import services
from src.admin.dependencies import require_admin
from src.auth.schemas import UserCreate
from src.database import get_session

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[require_admin])

router.post("/create-user")

SessionDep = Annotated[Session, Depends(get_session)]


def create_user(user_data: UserCreate, session: SessionDep):
    return services.create_user(user_data, session)
