from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.modules.auth.schema import AuthForgetPasswordSchema, DeviceSchema
from api.modules.auth.service import AuthService
from api.modules.user.model import User


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
  mock_auth_repo: MagicMock,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_user_role_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_password_service: MagicMock,
) -> AuthService:
  return AuthService(
    repository=mock_auth_repo,
    device_repository=mock_device_repo,
    user_repository=mock_user_repo,
    user_role_repository=mock_user_role_repo,
    jwt_service=mock_jwt_service,
    password_service=mock_password_service,
  )


def sample_forget_password_data(faker: Faker) -> dict:
  """
  Sample data for forget password request.
  """
  return {
    "email": faker.email(),
    "password": faker.password(),
    "uuid": faker.uuid4(),
    "device": DeviceSchema(
      client_device_id=faker.uuid4(),
      device_type=faker.word(),
      os=faker.word(),
      browser=faker.word(),
      ip_address=faker.ipv4(),
      latitude=faker.latitude(),
      longitude=faker.longitude(),
    ),
  }


def test_forget_password_success(
  auth_service: AuthService,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_auth_repo: MagicMock,
  faker: Faker,
) -> None:
  """
  Test forget password success.
  """
  data = sample_forget_password_data(faker)
  forget_data = AuthForgetPasswordSchema(email=data["email"], device=data["device"])

  mock_user = User(id=1, email=data["email"], password=data["password"], uuid=data["uuid"])
  mock_user_repo.get_user_by_email.return_value = mock_user

  # Mock store_device to return a mock device with an ID
  mock_device = MagicMock(id=10)
  mock_device_repo.store_device.return_value = mock_device

  result = auth_service.forget_password(forget_data)

  assert result is True
  mock_user_repo.get_user_by_email.assert_called_once_with(data["email"])
  mock_jwt_service.create_token.assert_called_once()
  mock_device_repo.store_device.assert_called_once()
  mock_auth_repo.store_token.assert_called_once()


def test_forget_password_user_not_found(
  auth_service: AuthService,
  mock_device_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_auth_repo: MagicMock,
  faker: Faker,
) -> None:
  data = sample_forget_password_data(faker)
  forget_data = AuthForgetPasswordSchema(email=data["email"], device=data["device"])

  mock_user_repo.get_user_by_email.return_value = None

  result = auth_service.forget_password(forget_data)

  assert result is True  # Should return True even if user not found for security
  mock_jwt_service.create_token.assert_not_called()
  mock_device_repo.store_device.assert_not_called()
  mock_auth_repo.store_token.assert_not_called()
