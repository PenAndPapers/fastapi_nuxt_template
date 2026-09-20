import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Auth module related imports (services and repositories)
from api.modules.auth.jwt.service import JwtService, settings
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository, DeviceRepository
from api.modules.auth.service import AuthService
from api.modules.user.repository import UserRepository, UserRoleRepository

# Core module related imports
from core.database import SessionLocal
from main import app

env_path = find_dotenv(".env") or find_dotenv(".env.example")
if env_path:
  load_dotenv(env_path, override=True)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
  """
  Provides a database session for each test.
  Rolls back the transaction at the end to ensure test isolation.
  """
  session = SessionLocal()
  try:
    yield session
  finally:
    session.rollback()
    session.close()


@pytest.fixture
def mock_db_session() -> MagicMock:
  return MagicMock()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
  with TestClient(app) as c:
    yield c


@pytest.fixture()
def faker() -> Faker:
  return Faker()


# ---------------------------------------------------------------------------------------------------
# Auth module related fixtures
# ---------------------------------------------------------------------------------------------------
@pytest.fixture
def unit_mock_auth_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_device_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_user_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_user_role_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_jwt_service() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_password_service() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_auth_service(
  mock_db_session: MagicMock,
  unit_mock_auth_repo: MagicMock,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_user_role_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_password_service: MagicMock,
) -> AuthService:
  return AuthService(
    db=mock_db_session,
    repository=unit_mock_auth_repo,
    device_repository=unit_mock_device_repo,
    user_repository=unit_mock_user_repo,
    user_role_repository=unit_mock_user_role_repo,
    jwt_service=unit_mock_jwt_service,
    password_service=unit_mock_password_service,
  )


@pytest.fixture
def jwt_service(tmp_path: Path) -> JwtService:
  """Fixture to provide a properly configured JwtService with mock key files."""
  priv_file = tmp_path / "private_key.pem"
  pub_file = tmp_path / "public_key.pem"
  priv_file.write_text(os.getenv("TEST_JWT_PRIVATE_KEY", ""))
  pub_file.write_text(os.getenv("TEST_JWT_PUBLIC_KEY", ""))

  with (
    patch.object(settings, "private_key_path", priv_file),
    patch.object(settings, "public_key_path", pub_file),
  ):
    yield JwtService()


@pytest.fixture
def auth_service(db_session: Session, jwt_service: JwtService) -> AuthService:
  """Shared AuthService fixture automatically available across all tests."""
  return AuthService(
    db=db_session,
    repository=AuthRepository(db_session),
    device_repository=DeviceRepository(db_session),
    user_repository=UserRepository(db_session),
    user_role_repository=UserRoleRepository(db_session),
    jwt_service=jwt_service,
    password_service=PasswordService(),
  )
