import io
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
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


if __name__ == "__main__":
    unittest.main()
