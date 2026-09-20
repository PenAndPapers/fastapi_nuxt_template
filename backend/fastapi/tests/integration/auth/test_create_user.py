from unittest.mock import patch

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.jwt.service import JwtService
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository, DeviceRepository
from api.modules.auth.service import AuthService
from api.modules.user.exception import UserAlreadyExistExceptionError
from api.modules.user.model import Role, User, UserRole
from api.modules.user.repository import UserRepository, UserRoleRepository
from api.modules.user.schema import EnumUserRole, UserCreateSchema


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
  # We patch the read_text method of Path objects specifically during
  # the initialization of JwtService to avoid FileNotFoundError in CI
  with patch("pathlib.Path.read_text") as mock_read:
    mock_read.return_value = "fake-key-content"

    return AuthService(
      db=db_session,
      repository=AuthRepository(db_session),
      device_repository=DeviceRepository(db_session),
      user_repository=UserRepository(db_session),
      user_role_repository=UserRoleRepository(db_session),
      jwt_service=JwtService(),
      password_service=PasswordService(),
    )


def sample_data(db_session: Session, faker: Faker) -> dict[str, str]:
  session_id = hex(id(db_session))
  return {
    "email": f"test_integration_create_user_{session_id}_{faker.email()}",
    "password": faker.password(),
    "invalid_email": f"test_integration_create_user_{session_id}_{faker.email()}",
    "invalid_password": faker.password(),
    "uuid": faker.uuid4(),
    "token_val": faker.uuid4(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
  }


def test_create_user_integration_success(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)

  user_data = UserCreateSchema(
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    role=EnumUserRole.USER,
  )

  # Act
  created_user = auth_service.register(user_data)

  # Assert
  # 1. Verify user exists in database
  db_user = db_session.query(User).filter_by(email=data["email"]).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid
  assert db_user.password != data["password"]

  # Verify role association exists in junction table
  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.USER.value


def test_create_superadmin_integration_success(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)

  # Arrange: Create user data
  user_data = UserCreateSchema(
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    role=EnumUserRole.SUPER_ADMIN,
  )

  # Act
  created_user = auth_service.register(user_data)

  # Verify
  db_user = db_session.query(User).filter_by(email=data["email"]).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid
  assert db_user.password != data["password"]

  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.SUPER_ADMIN.value


def test_duplicate_email_integration_error(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_data(db_session, faker)

  # Arrange: Create user data
  first_user_data = UserCreateSchema(
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    role=EnumUserRole.SUPER_ADMIN,
  )

  # Act
  auth_service.register(first_user_data)

  # Verify
  db_user = db_session.query(User).filter_by(email=data["email"]).first()
  assert db_user is not None

  # Assert
  with pytest.raises(UserAlreadyExistExceptionError, match="A user with this email already exists"):
    second_user_data = UserCreateSchema(
      email=data["email"],
      password=data["password"],
      first_name=data["first_name"],
      last_name=data["last_name"],
      address=data["address"],
      phone_number=data["phone_number"],
      role=EnumUserRole.SUPER_ADMIN,
    )
    auth_service.register(second_user_data)
