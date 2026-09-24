import unittest
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.constants import Genders
from src.database import get_session
from src.exceptions_mapping import HTTP_ERROR_MAP
from src.patients.dependencies import valid_patient_id
from src.patients.exceptions import PatientNotFound
from src.patients.models import Patient


class PatientDependencyTest(unittest.TestCase):
    def test_lookup_uses_session_and_missing_patient_maps_to_404(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine, tables=[Patient.__table__])
        with Session(engine) as session:
            patient = Patient(
                first_name="Alex", last_name="Smith", age=30, gender=Genders.MALE
            )
            session.add(patient)
            session.commit()
            patient_id = patient.id

        app = FastAPI()

        def override_session():
            with Session(engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session

        @app.get("/{patient_id}")
        def lookup(patient: Annotated[Patient, Depends(valid_patient_id)]):
            return {"id": patient.id}

        with TestClient(app) as client:
            self.assertEqual(client.get(f"/{patient_id}").json(), {"id": patient_id})
            with self.assertRaises(PatientNotFound):
                client.get("/999")

        self.assertEqual(HTTP_ERROR_MAP[PatientNotFound][0], 404)
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
