from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.modules.auth.service import AuthService
from api.modules.user.model import User
from api.modules.user.schema import EnumUserRole, UserCreateSchema


@pytest.fixture
def mock_jwt_service() -> MagicMock:
  return MagicMock()


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


def sample_data(faker: Faker) -> dict:
  return {
    "uuid": faker.uuid4(),
    "email": faker.email(),
    "password": faker.password(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
    "role": EnumUserRole.USER,
  }


def test_regsiter_success(
  unit_mock_auth_service: AuthService,
  unit_mock_device_repo: MagicMock,
  unit_mock_password_service: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_user_role_repo: MagicMock,
  faker: Faker,
) -> None:
  # Generate sample data
  data = sample_data(faker)

  # Mock request data
  user_data = UserCreateSchema(
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    role=data["role"],
  )

  # Mock user repository create_user method return value
  unit_mock_user_repo.create_user.return_value = User(
    id=1,
    uuid=data["uuid"],
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
  )

  # Call the service method
  result = unit_mock_auth_service.register(user_data)

  # Assert
  # Check password was hashed
  unit_mock_password_service.password_hash.assert_called_once_with(data["password"])

  # Check user was created in repository
  unit_mock_user_repo.create_user.assert_called_once()

  # Check role was assigned
  unit_mock_user_role_repo.assign_role.assert_called_once_with(1, data["role"])

  # Check return values
  assert result.id == 1
  assert result.uuid == data["uuid"]
  assert result.email == data["email"]
  assert result.first_name == data["first_name"]
  assert result.last_name == data["last_name"]
  assert result.address == data["address"]
  assert result.phone_number == data["phone_number"]
