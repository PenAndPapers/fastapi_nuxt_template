from functools import lru_cache

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
  jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
  jwt_secret_key: str = Field(default="changeme", env="JWT_SECRET_KEY")
  access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
  refresh_token_expire_minutes: int = Field(default=1440, env="REFRESH_TOKEN_EXPIRE_MINUTES")
  password_reset_token_expire_minutes: int = Field(
    default=15, env="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES"
  )
  email_verification_token_expire_minutes: int = Field(
    default=10080, env="EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES"
  )
  otp_expire_seconds: int = Field(default=30, env="OTP_EXPIRE_SECONDS")
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
