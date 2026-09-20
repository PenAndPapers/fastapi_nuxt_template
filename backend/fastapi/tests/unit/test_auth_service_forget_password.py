from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.modules.auth.schema import FormAuthForgetPasswordSchema, FormDeviceSchema
from api.modules.auth.service import AuthService
from api.modules.user.model import User


@pytest.fixture
def unit_mock_password_service() -> MagicMock:
  return MagicMock()


@pytest.fixture
def unit_mock_jwt_service() -> MagicMock:
  service = MagicMock()
  service.get_token_jti.return_value = "family_123"
  service.create_token.return_value = MagicMock(
    encoded="token_val", exp=123456789, family_id="family_123"
  )
  return service


def sample_forget_password_data(faker: Faker) -> dict:
  """
  Sample data for forget password request.
  """
  return {
    "email": faker.email(),
    "password": faker.password(),
    "uuid": faker.uuid4(),
    "device": FormDeviceSchema(
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
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_auth_repo: MagicMock,
  faker: Faker,
) -> None:
  """
  Test forget password success.
  """
  data = sample_forget_password_data(faker)
  forget_data = FormAuthForgetPasswordSchema(email=data["email"], device=data["device"])

  mock_user = User(id=1, email=data["email"], password=data["password"], uuid=data["uuid"])
  unit_mock_user_repo.get_user_by_email.return_value = mock_user

  # Mock store_device to return a mock device with an ID
  mock_device = MagicMock(id=10)
  unit_mock_device_repo.store_device.return_value = mock_device

  result = unit_mock_auth_service.forget_password(forget_data)

  assert result is True
  unit_mock_user_repo.get_user_by_email.assert_called_once_with(data["email"])
  unit_mock_jwt_service.create_token.assert_called_once()
  unit_mock_device_repo.store_device.assert_called_once()
  unit_mock_auth_repo.store_token.assert_called_once()


def test_forget_password_user_not_found(
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_auth_repo: MagicMock,
  faker: Faker,
) -> None:
  data = sample_forget_password_data(faker)
  forget_data = FormAuthForgetPasswordSchema(email=data["email"], device=data["device"])

  unit_mock_user_repo.get_user_by_email.return_value = None

  result = unit_mock_auth_service.forget_password(forget_data)

  assert result is None  # Should return None if user not found
  unit_mock_jwt_service.create_token.assert_not_called()
  unit_mock_device_repo.store_device.assert_not_called()
  unit_mock_auth_repo.store_token.assert_not_called()
