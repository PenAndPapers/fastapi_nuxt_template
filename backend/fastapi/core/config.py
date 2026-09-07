from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = parent of backend/
# backend/fastapi/core/config.py -> backend/fastapi -> backend -> root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    # Load root .env first (shared by all services),
    # then backend/fastapi/.env can override locally (e.g. SQLite for tests).
    env_file=[
      str(PROJECT_ROOT / "backend" / "fastapi" / ".env"),
      str(PROJECT_ROOT / ".env"),
    ],
    extra="ignore",
    case_sensitive=False,
  )

  # ---- General ----
  app_name: str = Field(..., env="APP_NAME")
  app_env: str = Field(default="development", env="ENVIRONMENT")
  debug: bool = Field(default=False, env="BACKEND_DEBUG")
  api_prefix: str = Field(default="/api", env="BACKEND_API_PREFIX")

  # ---- Database ----
  database_url: str = Field(..., env="POSTGRES_URL")
  test_database_url: str | None = None

  # ---- Redis ----
  redis_url: str | None = None

  # ---- Security ----
  secret_key: str = Field(..., env="BACKEND_SECRET_KEY")
  allowed_origins: list[str] = Field(
    default_factory=lambda: [
      origin.strip() for origin in Settings.model_config.get("BACKEND_ALLOWED_ORIGINS").split(",")
    ]
  )


@lru_cache
def get_settings() -> Settings:
  return Settings()
