import unittest
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import jwt
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.auth.constants import JWT_ALGORITHM, Roles
from src.auth.dependencies import get_current_user
from src.auth.exceptions import (
    ForbiddenError,
    IncorrectPassword,
    InvalidJwtToken,
    UserAlreadyExist,
    UserNotFound,
)
from src.auth.models import User
from src.auth.schemas import SignIn, UserCreate
from src.auth.services import authenticated_user, create_user, generate_access_token
from src.config import settings
from src.database import get_session
from src.main import app


class SessionStub:
    def __init__(self, existing=None):
        self.existing = existing
        self.add = Mock()
        self.commit = Mock()
        self.refresh = Mock(side_effect=lambda user: setattr(user, "id", 7))

    def exec(self, _statement):
        return SimpleNamespace(first=lambda: self.existing)


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.credentials = SignIn(email="user@example.com", password="Valid123!")

    def test_password_validation(self):
        for password in (
            "short", "lowercase1!", "UPPERCASE1!", "NoNumber!",
            "NoSymbol1", "Valid 123!",
        ):
            with self.subTest(password=password), self.assertRaises(ValidationError):
                SignIn(email="user@example.com", password=password)
        with self.assertRaises(ValidationError):
            UserCreate(email="bad-email", role=Roles.USER, password="Valid123!")

    def test_create_user_and_duplicate(self):
        session = SessionStub()
        data = UserCreate(email="new@example.com", role=Roles.DOCTOR, password="Valid123!")
        with patch("src.auth.services.password_hash.hash", return_value="hashed"):
            user = create_user(data, session)
        self.assertEqual(
            (user.id, user.email, user.password_hash, user.role),
            (7, data.email, "hashed", Roles.USER),
        )
        session.add.assert_called_once_with(user)
        session.commit.assert_called_once()

        duplicate = SessionStub(user)
        with self.assertRaises(UserAlreadyExist):
            create_user(data, duplicate)
        duplicate.add.assert_not_called()

    def test_authenticate_success_and_failures(self):
        user = SimpleNamespace(id=7, role=Roles.DOCTOR, password_hash="hashed")
        with self.assertRaises(UserNotFound):
            authenticated_user(self.credentials, SessionStub())
        with patch("src.auth.services.password_hash.verify", return_value=False):
            with self.assertRaises(IncorrectPassword):
                authenticated_user(self.credentials, SessionStub(user))
        with patch("src.auth.services.password_hash.verify", return_value=True):
            self.assertIs(authenticated_user(self.credentials, SessionStub(user)), user)
            user.role = Roles.USER
            with self.assertRaises(ForbiddenError):
                authenticated_user(self.credentials, SessionStub(user))

    def test_token_round_trip_and_rejection(self):
        data = {"sub": "7", "role": Roles.ADMIN.value}
        token = generate_access_token(data, timedelta(minutes=5))
        claims = jwt.decode(
            token.access_token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        self.assertEqual((claims["sub"], claims["role"]), ("7", Roles.ADMIN))
        self.assertEqual(
            get_current_user(SimpleNamespace(credentials=token.access_token)),
            {"id": "7", "role": Roles.ADMIN},
        )
        default_token = generate_access_token(data, None)
        self.assertEqual(
            jwt.decode(
                default_token.access_token,
                settings.JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )["sub"],
            "7",
        )
        for invalid in (
            "invalid",
            jwt.encode({"role": 1}, settings.JWT_SECRET, algorithm=JWT_ALGORITHM),
            generate_access_token(data, timedelta(seconds=-1)).access_token,
        ):
            with self.subTest(invalid=invalid), self.assertRaises(InvalidJwtToken):
                get_current_user(SimpleNamespace(credentials=invalid))

    def test_sign_in_http_contract(self):
        session = SessionStub()
        app.dependency_overrides[get_session] = lambda: session
        try:
            with TestClient(app) as client, patch(
                "src.auth.router.authenticated_user"
            ) as authenticate:
                authenticate.return_value = SimpleNamespace(id=7, role=Roles.ADMIN)
                body = self.credentials.model_dump(mode="json")
                response = client.post("/auth/sign-in", json=body)
                self.assertEqual(response.status_code, 200)
                claims = jwt.decode(
                    response.json()["access_token"],
                    settings.JWT_SECRET,
                    algorithms=[JWT_ALGORITHM],
                )
                self.assertEqual(claims["sub"], "7")
                self.assertIn("expired_at", response.json())
                invalid = {"email": "bad", "password": "x"}
                self.assertEqual(
                    client.post("/auth/sign-in", json=invalid).status_code, 422
                )
                authenticate.side_effect = UserNotFound()
                response = client.post("/auth/sign-in", json=body)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["www-authenticate"], "Bearer")
        finally:
            app.dependency_overrides.clear()

    def test_create_then_sign_in_with_database(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine, tables=[User.__table__])

        def override_session():
            with Session(engine) as session:
                yield session

        app.dependency_overrides[get_session] = override_session
        try:
            with Session(engine) as session:
                user = create_user(
                    UserCreate(
                        email=self.credentials.email,
                        role=Roles.DOCTOR,
                        password=self.credentials.password,
                    ),
                    session,
                )
                self.assertNotEqual(user.password_hash, self.credentials.password)
                self.assertEqual(user.role, Roles.USER)
                with self.assertRaises(UserAlreadyExist):
                    create_user(
                        UserCreate(
                            email=self.credentials.email,
                            role=Roles.USER,
                            password=self.credentials.password,
                        ),
                        session,
                    )

            with TestClient(app) as client:
                response = client.post(
                    "/auth/sign-in", json=self.credentials.model_dump(mode="json")
                )
                self.assertEqual(response.status_code, 403)
                with Session(engine) as session:
                    user = session.get(User, 1)
                    user.role = Roles.DOCTOR
                    session.add(user)
                    session.commit()
                response = client.post(
                    "/auth/sign-in", json=self.credentials.model_dump(mode="json")
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    jwt.decode(
                        response.json()["access_token"],
                        settings.JWT_SECRET,
                        algorithms=[JWT_ALGORITHM],
                    )["sub"],
                    "1",
                )
                self.assertEqual(
                    client.post(
                        "/auth/sign-in",
                        json={"email": self.credentials.email, "password": "Wrong123!"},
                    ).status_code,
                    401,
                )
        finally:
            app.dependency_overrides.clear()
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
