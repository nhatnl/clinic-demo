from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.admin.router import router as admin_router
from src.auth.router import router as auth_router
from src.consultations.router import router as consultation_router
from src.diagnosis.router import router as diagnosis_router
from src.exceptions import Error
from src.exceptions_mapping import HTTP_ERROR_MAP
from src.patients.router import router as patients_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(diagnosis_router)
app.include_router(consultation_router)
app.include_router(patients_router)


@app.exception_handler(Error)
def handler_application_error(_request: Request, exc: Error) -> JSONResponse:
    status_code, detail, headers = HTTP_ERROR_MAP.get(
        type(exc),
        (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
            None,
        ),
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers=headers,
    )
