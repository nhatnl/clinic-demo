from fastapi import APIRouter

from src.admin.dependencies import require_admin
from src.auth.schemas import CreateUser

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[require_admin])

router.post("/create-user")


async def create_user(user_data: CreateUser):
    pass
