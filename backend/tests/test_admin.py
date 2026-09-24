import json
import unittest
from datetime import timedelta
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from src.auth.constants import Roles
from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.services import generate_access_token
from src.database import get_session
from src.logs.exceptions import InvalidDataField
from src.logs.models import ActivitiesLog
from src.logs.schemas import ActivityLogCreate
from src.logs.services import create_activity_log
from src.main import app


class AdminTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(
            self.engine, tables=[User.__table__, ActivitiesLog.__table__]
        )
        with Session(self.engine) as session:
            session.add(
                User(
                    id=1, email="admin@example.com", role=Roles.ADMIN,
                    password_hash="seed",
                )
            )
            session.commit()

        def override_session():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        self.client = TestClient(app)
        self.body = UserCreate(
            email="new@example.com", role=Roles.DOCTOR, password="Valid123!"
        ).model_dump(mode="json")

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    @staticmethod
    def headers(user_id, role):
        token = generate_access_token(
            {"sub": str(user_id), "role": role.value}, timedelta(minutes=5)
        ).access_token
        return {"Authorization": f"Bearer {token}"}

    def test_permissions_validation_and_atomic_creation(self):
        self.assertEqual(self.client.post("/admin/create-user", json=self.body).status_code, 401)
        self.assertEqual(
            self.client.post(
                "/admin/create-user", json=self.body,
                headers={"Authorization": "Bearer malformed"},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                "/admin/create-user", json=self.body,
                headers=self.headers(2, Roles.USER),
            ).status_code,
            403,
        )
        headers = self.headers(1, Roles.ADMIN)
        self.assertEqual(
            self.client.post(
                "/admin/create-user", json={"email": "bad"}, headers=headers
            ).status_code,
            422,
        )

        response = self.client.post("/admin/create-user", json=self.body, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], self.body["email"])
        self.assertEqual(response.json()["role"], Roles.DOCTOR)
        self.assertNotIn("password_hash", response.json())

        with Session(self.engine) as session:
            users = session.exec(select(User)).all()
            logs = session.exec(select(ActivitiesLog)).all()
            self.assertEqual(len(users), 2)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].user_id, 1)
            self.assertEqual(
                logs[0].data,
                {"created_user_id": response.json()["id"], "email": self.body["email"]},
            )
            json.dumps(logs[0].data)
            self.assertNotEqual(users[1].password_hash, self.body["password"])

        duplicate = self.client.post("/admin/create-user", json=self.body, headers=headers)
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(duplicate.json(), {"detail": "User already exists"})
        with Session(self.engine) as session:
            self.assertEqual(len(session.exec(select(User)).all()), 2)
            self.assertEqual(len(session.exec(select(ActivitiesLog)).all()), 1)

    def test_activity_log_validation_and_service(self):
        data = ActivityLogCreate(event="Admin Add User", user_id=1, data={"id": 8})
        session = Mock()
        create_activity_log(data, session)
        log = session.add.call_args.args[0]
        self.assertEqual((log.event, log.user_id, log.data), ("Admin Add User", 1, {"id": 8}))
        session.commit.assert_called_once()
        with self.assertRaises(InvalidDataField):
            ActivityLogCreate(event="Admin Add User", user_id=1, data={})
        for invalid in (
            {"event": "x", "user_id": 1, "data": {"id": 8}},
            {"event": "Admin Add User", "user_id": 0, "data": {"id": 8}},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                ActivityLogCreate(**invalid)

    def test_failed_log_rolls_back_new_user(self):
        with patch(
            "src.admin.services.create_activity_log", side_effect=RuntimeError("log failed")
        ):
            with self.assertRaisesRegex(RuntimeError, "log failed"):
                self.client.post(
                    "/admin/create-user",
                    json=self.body,
                    headers=self.headers(1, Roles.ADMIN),
                )
        with Session(self.engine) as session:
            self.assertEqual(len(session.exec(select(User)).all()), 1)
            self.assertEqual(len(session.exec(select(ActivitiesLog)).all()), 0)


if __name__ == "__main__":
    unittest.main()
