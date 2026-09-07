import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the project root in a way that works both on the developer host and
# inside the Docker container.
#
# On the host:
#   backend/fastapi/core/config.py -> backend/fastapi -> backend -> root
#   parents[3] = repo root
#
# Inside Docker (WORKDIR=/app):
#   /app/core/config.py -> parents[0..2] -> parents[3] raises IndexError
#   PROJECT_ROOT env var (set in Dockerfile) takes precedence.
def _resolve_project_root() -> Path:
  env_root = os.getenv("PROJECT_ROOT")
  if env_root:
    return Path(env_root)
  try:
    return Path(__file__).resolve().parents[3]
  except IndexError:
    # Fallback: assume the file lives at <root>/core/config.py
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _resolve_project_root()


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    # Load root .env first (shared by all services),
    # then backend/fastapi/.env can override locally (e.g. SQLite for tests).
    env_file=[
      str(PROJECT_ROOT / "backend" / "fastapi" / ".env"),
      str(PROJECT_ROOT / ".env"),
    ],
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
  )

  # ---- App ----
  app_name: str = Field(default="FastAPI App", env="APP_NAME")
  app_env: str = Field(default="development", env="ENVIRONMENT")
  debug: bool = Field(default=False, env="BACKEND_DEBUG")
  api_prefix: str = Field(default="/api", env="BACKEND_API_PREFIX")

  # ---- PostgreSQL ----
  postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
  postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
  postgres_user: str = Field(default="postgres_user", env="POSTGRES_USER")
  postgres_password: str = Field(default="changeme", env="POSTGRES_PASSWORD")
  postgres_db: str = Field(default="postgres_db", env="POSTGRES_DB")

  @computed_field  # type: ignore[prop-decorator]
  @property
  def database_url(self) -> str:
    """Composed SQLAlchemy URL for the application database."""
    return (
      f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
      f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    )

  test_database_url: str | None = Field(default=None, env="TEST_DATABASE_URL")

  # ---- Redis ----
  redis_host: str = Field(default="localhost", env="REDIS_HOST")
  redis_port: int = Field(default=6379, env="REDIS_PORT")
  redis_password: str | None = Field(default=None, env="REDIS_PASSWORD")

  @computed_field  # type: ignore[prop-decorator]
  @property
  def redis_url(self) -> str:
    """Composed Redis URL with optional auth."""
    auth = f":{self.redis_password}@" if self.redis_password else ""
    return f"redis://{auth}{self.redis_host}:{self.redis_port}/0"

  # ---- Security ----
  secret_key: str = Field(default="changeme", env="BACKEND_SECRET_KEY")
  allowed_origins: list[str] = Field(
    default_factory=lambda: [
      "http://localhost:3000",
      "http://localhost:8080",
    ],
    env="BACKEND_ALLOWED_ORIGINS",
  )


@lru_cache
def get_settings() -> Settings:
  return Settings()
