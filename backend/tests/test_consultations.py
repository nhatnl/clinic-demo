import unittest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.consultations.models import Consultation, ConsultationDiagnosis
from src.database import get_session
from src.diagnosis.model import Diagnosis
from src.main import app
from src.patients.models import Patient


class ConsultationApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(
            cls.engine,
            tables=[
                Patient.__table__,
                Diagnosis.__table__,
                Consultation.__table__,
                ConsultationDiagnosis.__table__,
            ],
        )

        with Session(cls.engine) as session:
            session.add(Patient(id=1, name="An Nguyen", age=32))
            session.add(
                Diagnosis(
                    code="A00.0",
                    name="Cholera due to Vibrio cholerae 01",
                    description="Cholera due to Vibrio cholerae 01, biovar cholerae",
                    is_valid_for_submission=True,
                )
            )
            session.commit()

        def override_session():
            with Session(cls.engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.clear()
        cls.engine.dispose()

    def test_create_list_search_and_missing_reference(self) -> None:
        created = self.client.post(
            "/consultation",
            json={
                "patient_id": 1,
                "note": "  Prescribe oral rehydration  ",
                "diagnosis_codes": ["a00.0"],
            },
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["note"], "Prescribe oral rehydration")
        self.assertEqual(created.json()["patient"]["name"], "An Nguyen")
        self.assertEqual(created.json()["diagnoses"][0]["code"], "A00.0")

        listed = self.client.get(
            "/consultation",
            params={"patient": "nguyen", "diagnosis_code": "a00.0"},
        )
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

        missing = self.client.post(
            "/consultation",
            json={
                "patient_id": 1,
                "note": "Unknown diagnosis",
                "diagnosis_codes": ["Z99.9"],
            },
        )
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json(), {"detail": "Diagnosis code not found"})

        missing_patient = self.client.post(
            "/consultation",
            json={
                "patient_id": 99,
                "note": "Unknown patient",
                "diagnosis_codes": ["A00.0"],
            },
        )
        self.assertEqual(missing_patient.status_code, 404)
        self.assertEqual(missing_patient.json(), {"detail": "Patient not found"})

        duplicate_codes = self.client.post(
            "/consultation",
            json={
                "patient_id": 1,
                "note": "Duplicate diagnoses",
                "diagnosis_codes": ["A00.0", "a00.0"],
            },
        )
        self.assertEqual(duplicate_codes.status_code, 422)


if __name__ == "__main__":
    unittest.main()
