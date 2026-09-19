from unittest.mock import MagicMock

import pytest

from api.modules.auth.exception import InvalidCredentialsError
from api.modules.auth.schema import AuthLoginSchema, SessionToken
from api.modules.auth.service import AuthService
from api.modules.user.model import User


@pytest.fixture()
def mock_db_session() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_auth_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_device_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_role_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_jwt_service() -> MagicMock:
  service = MagicMock()
  service.get_token_jti.return_value = "family_123"
  service.create_token.return_value = MagicMock(
    encoded="token_val", exp=123456789, family_id="family_123"
  )
  return service


@pytest.fixture
def mock_password_service() -> MagicMock:
  return MagicMock()


@pytest.fixture
def auth_service(
  mock_db_session: MagicMock,
  mock_auth_repo: MagicMock,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_user_role_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_password_service: MagicMock,
) -> AuthService:
  return AuthService(
    db=mock_db_session,
    repository=mock_auth_repo,
    device_repository=mock_device_repo,
    user_repository=mock_user_repo,
    user_role_repository=mock_user_role_repo,
    jwt_service=mock_jwt_service,
    password_service=mock_password_service,
  )


def sample_data() -> dict[str, str]:
  return {
    "email": "test@example.com",
    "nonexistent_email": "nonexistent@example.com",
    "password": "password123",
    "hashed_password": "hashed_password",
    "invalid_password": "wrong_password",
    "uuid": "user-uuid-123",
    "token_val": "token_val",
  }


def test_login_success(
  auth_service: AuthService,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_password_service: MagicMock,
  mock_jwt_service: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = AuthLoginSchema(email=data["email"], password=data["password"])
  mock_user = User(id=1, email=data["email"], password=data["hashed_password"], uuid=data["uuid"])
  mock_user_repo.get_user_by_email.return_value = mock_user
  mock_password_service.verify_password.return_value = True

  # Act
  result = auth_service.login(login_data)

  # Assert
  assert isinstance(result, SessionToken)
  assert str(result.access_token) == data["token_val"]
  mock_user_repo.get_user_by_email.assert_called_once_with(data["email"])
  mock_password_service.verify_password.assert_called_once_with(
    data["password"], data["hashed_password"]
  )
  assert mock_jwt_service.create_token.call_count == 2


def test_login_failed_invalid_password(
  auth_service: AuthService,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_password_service: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = AuthLoginSchema(email=data["email"], password=data["invalid_password"])
  mock_user = User(id=1, email=data["email"], password=data["hashed_password"], uuid=data["uuid"])
  mock_user_repo.get_user_by_email.return_value = mock_user
  mock_password_service.verify_password.return_value = False

  # Act & Assert
  with pytest.raises(InvalidCredentialsError):
    auth_service.login(login_data)


def test_login_failed_user_not_found(
  auth_service: AuthService,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = AuthLoginSchema(email=data["nonexistent_email"], password=data["password"])
  mock_user_repo.get_user_by_email.return_value = None

  # Act & Assert
  with pytest.raises(InvalidCredentialsError):
    auth_service.login(login_data)
