import io
import re
import runpy
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from pwdlib import PasswordHash
from sqlmodel import SQLModel, create_engine

from src.main import app  # noqa: F401 - imports the models registered by the API


class MigrationTests(unittest.TestCase):
    def test_postgres_migrations_create_every_api_table(self):
        output = io.StringIO()
        config = Config(
            Path(__file__).resolve().parents[1] / "alembic.ini",
            output_buffer=output,
        )
        with patch.dict("os.environ", {"ADMIN_PASSWORD": "Valid123!"}):
            command.upgrade(config, "head", sql=True)
        sql = output.getvalue()
        for table in SQLModel.metadata.tables:
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE {table}", sql)
        self.assertIn("CREATE TYPE genders AS ENUM", sql)
        self.assertIn("ALTER TABLE patients ADD COLUMN gender genders", sql)
        self.assertIn("'admin@kyanon.digital'", sql)
        self.assertIn("'ACTIVE'", sql)
        self.assertIn("'ADMIN'", sql)
        self.assertIn("ALTER TABLE consultations ADD COLUMN created_by_id INTEGER", sql)
        self.assertIn("FOREIGN KEY(created_by_id) REFERENCES users (id)", sql)
        admin_hash = re.search(r"\$argon2id\$[^']+", sql)
        self.assertIsNotNone(admin_hash)
        self.assertFalse(PasswordHash.recommended().verify("Admin@123", admin_hash.group()))
        self.assertIn("WHERE NOT EXISTS (SELECT 1 FROM users", sql)

    def test_admin_bootstrap_and_rotation(self):
        migration = runpy.run_path(
            str(
                Path(__file__).resolve().parents[1]
                / "alembic/versions/d20260925_bootstrap_admin.py"
            )
        )
        engine = create_engine("sqlite://")
        with engine.begin() as connection:
            connection.execute(
                sa.text("""CREATE TABLE users (
                    email TEXT, password_hash TEXT, created_at TEXT, updated_at TEXT,
                    status TEXT, role TEXT)""")
            )
            with (
                patch("alembic.op.execute", side_effect=connection.execute),
                patch.dict("os.environ", {"ADMIN_PASSWORD": "Valid123!"}),
            ):
                migration["upgrade"]()
            stored = connection.execute(
                sa.text("SELECT password_hash FROM users WHERE email = 'admin@kyanon.digital'")
            ).scalar_one()
            self.assertTrue(PasswordHash.recommended().verify("Valid123!", stored))

            output = io.StringIO()
            with (
                patch("alembic.op.execute", side_effect=connection.execute),
                patch.dict("os.environ", {"ADMIN_PASSWORD": ""}),
                patch("secrets.token_urlsafe", return_value="abcdef0123456789"),
                redirect_stderr(output),
            ):
                migration["upgrade"]()
            stored = connection.execute(
                sa.text("SELECT password_hash FROM users WHERE email = 'admin@kyanon.digital'")
            ).scalar_one()
            self.assertTrue(PasswordHash.recommended().verify("Aa1!abcdef0123456789", stored))
            self.assertIn("Aa1!abcdef0123456789", output.getvalue())
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
