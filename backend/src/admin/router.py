from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from src.admin import services
from src.admin.dependencies import require_admin
from src.admin.schemas import UserResponse
from src.auth.schemas import UserCreate
from src.database import get_session

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    session: SessionDep,
    admin: Annotated[dict, Depends(require_admin)],
):
    return services.admin_create_user(user_data, session, int(admin["id"]))
