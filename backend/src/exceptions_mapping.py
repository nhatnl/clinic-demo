from fastapi import status

from src.auth import exceptions as auth_exceptions
from src.consultations import exceptions as consultation_exceptions

HTTP_ERROR_MAP = {
    auth_exceptions.UserNotFound: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
    auth_exceptions.IncorrectPassword: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
    auth_exceptions.InvalidJwtToken: (
        status.HTTP_401_UNAUTHORIZED,
        "Invalid authentication credentials",
        {"WWW-Authenticate": "Bearer"},
    ),
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
    consultation_exceptions.DiagnosisNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Diagnosis code not found",
        None,
    ),
}
