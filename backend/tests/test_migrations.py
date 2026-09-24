import io
import re
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from pwdlib import PasswordHash
from sqlmodel import SQLModel

from src.main import app  # noqa: F401 - imports the models registered by the API


class MigrationTests(unittest.TestCase):
    def test_postgres_migrations_create_every_api_table(self):
        output = io.StringIO()
        config = Config(
            Path(__file__).resolve().parents[1] / "alembic.ini",
            output_buffer=output,
        )
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
        self.assertTrue(PasswordHash.recommended().verify("Admin@123", admin_hash.group()))


if __name__ == "__main__":
    unittest.main()
