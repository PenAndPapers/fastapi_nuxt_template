from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FastAPI App"
    app_env: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = Field(..., env="POSTGRES_URL")
    test_database_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
