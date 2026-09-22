from fastapi import APIRouter

router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])

router.get(
    "/",
)


def get_diagnosis():
    pass
