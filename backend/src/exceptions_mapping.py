from fastapi import status

from src.auth import exceptions as auth_exceptions
from src.consultations import exceptions as consultation_exceptions
from src.patients import exceptions as patient_exceptions

INVALID_CREDENTIALS = (
    status.HTTP_401_UNAUTHORIZED,
    "Invalid authentication credentials",
    {"WWW-Authenticate": "Bearer"},
)

HTTP_ERROR_MAP = {
    auth_exceptions.UserNotFound: INVALID_CREDENTIALS,
    auth_exceptions.IncorrectPassword: INVALID_CREDENTIALS,
    auth_exceptions.InvalidJwtToken: INVALID_CREDENTIALS,
    auth_exceptions.UserAlreadyExist: (
        status.HTTP_400_BAD_REQUEST,
        "User already exists",
        None,
    ),
    consultation_exceptions.PatientNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Patient not found",
        None,
    ),
    patient_exceptions.PatientNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Patient not found",
        None,
    ),
    consultation_exceptions.DiagnosisNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Diagnosis code not found",
        None,
    ),
    consultation_exceptions.ConsultationNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Consultation not found",
        None,
    ),
    auth_exceptions.ForbiddenError: (
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to perform this action",
        None,
    ),
}
