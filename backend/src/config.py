from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )

    JWT_SECRET: str = "this-must-be-changed"
    JWT_ACCESS_TOKEN_EXPIRE_DURATION: int = 60


settings = Config()
