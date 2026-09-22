from fastapi import APIRouter

from src.auth.schemas import SignIn, Token

router = APIRouter(prefix="/auth", tags=["auth"])

router.post("/sign-in", response_model=Token)


def sign_in(sign_in_data: SignIn):
    pass
