from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.modules.auth.service import AuthService
from api.modules.user.model import User
from api.modules.user.schema import EnumUserRole, UserCreateSchema


@pytest.fixture
def mock_auth_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_role_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_jwt_service() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_password_service() -> MagicMock:
  # We use a real PasswordService or a mock, but for unit tests, a mock is faster
  service = MagicMock()
  service.password_hash.return_value = "hashed_password_123"
  return service


@pytest.fixture
def auth_service(
  mock_auth_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_user_role_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_password_service: MagicMock,
) -> AuthService:
  return AuthService(
    repository=mock_auth_repo,
    user_repository=mock_user_repo,
    user_role_repository=mock_user_role_repo,
    jwt_service=mock_jwt_service,
    password_service=mock_password_service,
  )


def test_create_user_success(
  auth_service: AuthService,
  mock_password_service: MagicMock,
  mock_user_repo: MagicMock,
  mock_user_role_repo: MagicMock,
  faker: Faker,
) -> None:
  uuid = faker.uuid4()
  email = faker.email()
  password = faker.password()
  first_name = faker.first_name()
  last_name = faker.last_name()
  address = faker.address()
  phone_number = faker.phone_number()
  role = EnumUserRole.USER

  # Mock request data
  user_data = UserCreateSchema(
    email=email,
    password=password,
    first_name=first_name,
    last_name=last_name,
    address=address,
    phone_number=phone_number,
    role=role,
  )

  # Mock user repository create_user method return value
  mock_user_repo.create_user.return_value = User(
    id=1,
    uuid=uuid,
    email=email,
    password=password,
    first_name=first_name,
    last_name=last_name,
    address=address,
    phone_number=phone_number,
  )

  # Call the service method
  result = auth_service.register(user_data)

  # Assert
  # Check password was hashed
  mock_password_service.password_hash.assert_called_once_with(password)

  # Check user was created in repository
  mock_user_repo.create_user.assert_called_once()

  # Check role was assigned
  mock_user_role_repo.assign_role.assert_called_once_with(1, role)

  # Check return values
  assert result.id == 1
  assert result.uuid == uuid
  assert result.email == email
  assert result.first_name == first_name
  assert result.last_name == last_name
  assert result.address == address
  assert result.phone_number == phone_number
