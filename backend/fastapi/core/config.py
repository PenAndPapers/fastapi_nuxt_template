from functools import lru_cache
from pathlib import Path

from dotenv import find_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    # Automatically find the .env file in parent directories.
    # This works on both the developer host and inside the Docker container.
    env_file=find_dotenv(),
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
  )

  # ---- App ----
  app_name: str = Field(default="FastAPI App", alias="APP_NAME")
  app_env: str = Field(default="development", alias="ENVIRONMENT")
  debug: bool = Field(default=False, alias="BACKEND_DEBUG")
  api_prefix: str = Field(default="/api", alias="BACKEND_API_PREFIX")

  # ---- PostgreSQL ----
  postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
  postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
  postgres_user: str = Field(default="postgres_user", alias="POSTGRES_USER")
  postgres_password: str = Field(default="changeme", alias="POSTGRES_PASSWORD")
  postgres_db: str = Field(default="postgres_db", alias="POSTGRES_DB")

  @computed_field  # type: ignore[prop-decorator]
  @property
  def database_url(self) -> str:
    """Composed SQLAlchemy URL for the application database."""
    return (
      f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
      f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    )

  # ---- Redis ----
  redis_host: str = Field(default="localhost", alias="REDIS_HOST")
  redis_port: int = Field(default=6379, alias="REDIS_PORT")
  redis_password: str | None = Field(default=None, alias="REDIS_PASSWORD")

  @computed_field  # type: ignore[prop-decorator]
  @property
  def redis_url(self) -> str:
    """Composed Redis URL with optional auth."""
    auth = f":{self.redis_password}@" if self.redis_password else ""
    return f"redis://{auth}{self.redis_host}:{self.redis_port}/0"

  # ---- Security ----
  jwt_algorithm: str = Field(default="ES256", alias="JWT_ALGORITHM")
  jwt_issuer: str = Field(default="http://localhost:8000", alias="JWT_ISSUER")
  jwt_audience: str = Field(default="http://localhost:3000", alias="JWT_AUDIENCE")
  access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
  refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
  password_reset_token_expire_minutes: int = Field(
    default=15, alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES"
  )
  email_verification_token_expire_days: int = Field(
    default=7, alias="EMAIL_VERIFICATION_TOKEN_EXPIRE_DAYS"
  )
  otp_expire_seconds: int = Field(default=30, alias="OTP_EXPIRE_SECONDS")
  public_key_path: Path = Field(default_factory=lambda: Path("/app/certs/public_key.pem"))
  private_key_path: Path = Field(default_factory=lambda: Path("/app/certs/private_key.pem"))

  # ---- CORS ----
  allow_origins: str = Field(
    default="http://localhost:3000,http://localhost:8000,http://localhost:8080",
    alias="BACKEND_CORS_ALLOWED_ORIGINS",
  )
  allow_credentials: bool = Field(
    default=True,
    alias="BACKEND_CORS_CREDENTIALS",
  )
  allow_methods: str = Field(
    default="*",
    alias="BACKEND_CORS_ALLOW_METHODS",
  )
  allow_headers: str = Field(
    default="*",
    alias="BACKEND_CORS_ALLOW_HEADERS",
  )
  trusted_hosts: str = Field(
    default="localhost,127.0.0.1,testserver",
    alias="BACKEND_CORS_TRUSTED_HOSTS",
  )

  @property
  def origins_list(self) -> list[str]:
    return [item.strip() for item in self.allow_origins.split(",") if item.strip()]

  @property
  def methods_list(self) -> list[str]:
    return [item.strip() for item in self.allow_methods.split(",") if item.strip()]

  @property
  def headers_list(self) -> list[str]:
    return [item.strip() for item in self.allow_headers.split(",") if item.strip()]

  @property
  def trusted_hosts_list(self) -> list[str]:
    return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]

  # ---- Seeding ----
  seed_data: bool = Field(default=False, alias="BACKEND_SEED_DATA")


@lru_cache
def get_settings() -> Settings:
  return Settings()
