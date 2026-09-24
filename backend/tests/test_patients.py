import unittest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.auth.constants import Roles
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.constants import Genders
from src.database import get_session
from src.logs.models import ActivitiesLog
from src.main import app
from src.patients.models import Patient


class PatientSearchTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(
            self.engine,
            tables=[User.__table__, Patient.__table__, ActivitiesLog.__table__],
        )
        with Session(self.engine) as session:
            session.add(
                User(id=1, email="admin@example.com", role=Roles.ADMIN, password_hash="x")
            )
            session.add_all(
                [
                    Patient(first_name="An", last_name="Nguyen", age=32),
                    Patient(
                        first_name="Binh",
                        last_name="Tran",
                        age=45,
                        gender=Genders.MALE,
                    ),
                ]
            )
            session.commit()

        def override_session():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        app.dependency_overrides[get_current_user] = lambda: {
            "id": 1,
            "role": Roles.ADMIN,
        }
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_query_model_filters(self):
        response = self.client.get(
            "/patients/",
            params={"name": "nguyen", "age_from": 30, "age_to": 40},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["first_name"] for item in response.json()], ["An"])

        response = self.client.get("/patients/", params={"gender": "MALE"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["first_name"] for item in response.json()], ["Binh"])

    def test_query_model_validation(self):
        for params in (
            {"name": "ab"},
            {"age_from": 50, "age_to": 20},
            {"gender": "UNKNOWN"},
        ):
            with self.subTest(params=params):
                self.assertEqual(
                    self.client.get("/patients/", params=params).status_code,
                    422,
                )

    def test_create_uses_default_gender_and_rejects_server_fields(self):
        payload = {"first_name": "Chris", "last_name": "Smith", "age": 30}
        response = self.client.post("/patients/", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["gender"], Genders.NO_PROVIDED.value)
        self.assertIsNotNone(response.json()["id"])

        response = self.client.post("/patients/", json={**payload, "id": 999})
        self.assertEqual(response.status_code, 422)

    def test_update_only_changes_editable_fields(self):
        original = self.client.get("/patients/1").json()
        response = self.client.put("/patients/1", json={"first_name": "Alice"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first_name"], "Alice")
        self.assertEqual(response.json()["last_name"], original["last_name"])
        self.assertEqual(response.json()["id"], original["id"])
        self.assertEqual(response.json()["created_at"], original["created_at"])

        for field, value in (
            ("id", 999),
            ("created_at", "2020-01-01T00:00:00Z"),
            ("updated_at", "2020-01-01T00:00:00Z"),
            ("first_name", None),
        ):
            with self.subTest(field=field):
                self.assertEqual(
                    self.client.put("/patients/1", json={field: value}).status_code,
                    422,
                )


if __name__ == "__main__":
    unittest.main()
