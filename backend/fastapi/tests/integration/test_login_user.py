from pathlib import Path
from unittest.mock import patch

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.jwt.service import JwtService
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository
from api.modules.auth.schema import AuthLoginSchema, SessionToken
from api.modules.auth.service import AuthService
from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository
from core.config import get_settings

settings = get_settings()

# Create valid fixture keys (with 5 hyphens)
MOCK_PRIVATE_KEY = (
  "-----BEGIN EC PRIVATE KEY-----\n"
  "MHcCAQEEIG2KLeKlBGvqsgYuONt25EYRWeUqnAuEeYaRWI5vMyvUoAoGCCqGSM49\n"
  "AwEHoUQDQgAEIOmFjFCnGcB+thM1BN/sTm/RQpCGOo9Atwmh+1Vl+jsIeBYUnMEQ\n"
  "U9Sg4VTlVQsl+1uwtPR+TQoFQv7j1OVu7Q==\n"
  "-----END EC PRIVATE KEY-----\n"
)

MOCK_PUBLIC_KEY = (
  "-----BEGIN PUBLIC KEY-----\n"
  "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIOmFjFCnGcB+thM1BN/sTm/RQpCG\n"
  "Oo9Atwmh+1Vl+jsIeBYUnMEQU9Sg4VTlVQsl+1uwtPR+TQoFQv7j1OVu7Q==\n"
  "-----END PUBLIC KEY-----\n"
)


@pytest.fixture
def auth_service(db_session: Session, tmp_path: Path) -> AuthService:
  # 1. Create temporary PEM files in the test runner isolated directory
  priv_file = tmp_path / "private_key.pem"
  pub_file = tmp_path / "public_key.pem"
  priv_file.write_text(MOCK_PRIVATE_KEY)
  pub_file.write_text(MOCK_PUBLIC_KEY)

  # 2. Import the settings instance specifically from the jwt service module
  from api.modules.auth.jwt.service import settings

  # 3. Patch the Path attributes ON THAT SETTINGS INSTANCE before JwtService() is called
  with (
    patch.object(settings, "private_key_path", priv_file),
    patch.object(settings, "public_key_path", pub_file),
  ):
    # When JwtService runs, settings.private_key_path will point to priv_file
    jwt_service = JwtService()

    return AuthService(
      repository=AuthRepository(db_session),
      user_repository=UserRepository(db_session),
      user_role_repository=UserRoleRepository(db_session),
      jwt_service=jwt_service,
      password_service=PasswordService(),
    )


def sample_data(db_session: Session, faker: Faker) -> dict[str, str]:
  session_id = hex(id(db_session))

  return {
    "email": f"test_integration_login_function_{session_id}_{faker.email()}",
    "password": faker.password(),
    "invalid_email": f"test_integration_login_function_{session_id}_{faker.email()}",
    "invalid_password": faker.password(),
    "uuid": faker.uuid4(),
    "token_val": faker.uuid4(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
  }


def test_login_success_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)
  # Arrange: Create a user in the DB first
  password = data["password"]
  hashed_pw = PasswordService().password_hash(password)

  test_user = User(
    email=data["email"],
    password=hashed_pw,
    uuid=data["uuid"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
  )
  db_session.add(test_user)
  db_session.commit()

  login_data = AuthLoginSchema(email=data["email"], password=password)

  # Act
  result = auth_service.login(login_data)

  # Assert
  assert isinstance(result, SessionToken)
  assert result.access_token is not None
  assert result.refresh_token is not None
  assert result.access_exp > 0
  assert result.refresh_exp > 0


def test_login_failed_invalid_password_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)
  # Arrange
  password = data["password"]
  hashed_pw = PasswordService().password_hash(password)

  test_user = User(
    email=data["email"],
    password=hashed_pw,
    uuid=data["uuid"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
  )
  db_session.add(test_user)
  db_session.commit()

  login_data = AuthLoginSchema(email=data["email"], password=data["invalid_password"])

  # Act & Assert
  from api.modules.auth.exception import InvalidCredentialsError

  with pytest.raises(InvalidCredentialsError, match="Incorrect email or password"):
    auth_service.login(login_data)


def test_login_failed_user_not_found_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)
  # Arrange
  password = data["password"]
  hashed_pw = PasswordService().password_hash(password)

  test_user = User(
    email=data["email"],
    password=hashed_pw,
    uuid=data["uuid"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
  )
  db_session.add(test_user)
  db_session.commit()

  login_data = AuthLoginSchema(email=data["invalid_email"], password=data["password"])

  # Act & Assert
  from api.modules.auth.exception import InvalidCredentialsError

  with pytest.raises(InvalidCredentialsError, match="Incorrect email or password"):
    auth_service.login(login_data)
