from unittest.mock import MagicMock

import pytest

from api.modules.auth.exception import InvalidCredentialsError
from api.modules.auth.schema import FormAuthLoginSchema, SessionTokenResponseSchema
from api.modules.auth.service import AuthService
from api.modules.user.model import User


@pytest.fixture
def unit_mock_jwt_service() -> MagicMock:
  service = MagicMock()
  service.get_token_jti.return_value = "family_123"
  service.create_token.return_value = MagicMock(
    encoded="token_val", exp=123456789, family_id="family_123"
  )
  return service


def sample_data() -> dict[str, str]:
  return {
    "email": "test@example.com",
    "nonexistent_email": "nonexistent@example.com",
    "password": "P@ssword123",
    "invalid_password": "Wr0ng_pa$$word",
    "hashed_password": "hashed_password",
    "uuid": "user-uuid-123",
    "token_val": "token_val",
  }


def test_login_success(
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_password_service: MagicMock,
  unit_mock_jwt_service: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = FormAuthLoginSchema(email=data["email"], password=data["password"])
  mock_user = User(id=1, email=data["email"], password=data["hashed_password"], uuid=data["uuid"])
  unit_mock_auth_service.user_repository.get_user_by_email.return_value = mock_user
  unit_mock_password_service.verify_password.return_value = True

  # Act
  result = unit_mock_auth_service.login(login_data)

  # Assert
  assert isinstance(result, SessionTokenResponseSchema)
  assert str(result.access_token) == data["token_val"]
  unit_mock_auth_service.user_repository.get_user_by_email.assert_called_once_with(data["email"])
  unit_mock_password_service.verify_password.assert_called_once_with(
    data["password"], data["hashed_password"]
  )
  assert unit_mock_jwt_service.create_token.call_count == 2


def test_login_failed_invalid_password(
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_password_service: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = FormAuthLoginSchema(email=data["email"], password=data["invalid_password"])
  mock_user = User(id=1, email=data["email"], password=data["hashed_password"], uuid=data["uuid"])
  unit_mock_auth_service.user_repository.get_user.return_value = mock_user
  unit_mock_password_service.verify_password.return_value = False

  # Act & Assert
  with pytest.raises(InvalidCredentialsError):
    unit_mock_auth_service.login(login_data)


def test_login_failed_user_not_found(
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  login_data = FormAuthLoginSchema(email=data["nonexistent_email"], password=data["password"])
  unit_mock_auth_service.user_repository.get_user_by_email.return_value = None

  # Act & Assert
  with pytest.raises(InvalidCredentialsError):
    unit_mock_auth_service.login(login_data)
