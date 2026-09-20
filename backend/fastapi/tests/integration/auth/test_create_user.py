import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.service import AuthService
from api.modules.user.exception import UserAlreadyExistExceptionError
from api.modules.user.model import Role, User, UserRole
from api.modules.user.schema import EnumUserRole, UserCreateSchema


def _sample_data(db_session: Session, faker: Faker) -> dict[str, str]:
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


def _create_user_data(db_session: Session, faker: Faker, user_role: EnumUserRole) -> User:
  data = _sample_data(db_session, faker)

  user = UserCreateSchema(
    email=data["email"],
    password=data["password"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    role=user_role,
  )

  return user


def test_create_user_integration_success(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange: Create user data
  user_data = _create_user_data(db_session, faker, EnumUserRole.USER)

  # Act
  created_user = auth_service.register(user_data)

  # Assert
  # 1. Verify user exists in database
  db_user = db_session.query(User).filter_by(email=user_data.email).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid

  # Verify role association exists in junction table
  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.USER.value


def test_create_superadmin_integration_success(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:

  # Arrange: Create user data
  user_data = _create_user_data(db_session, faker, EnumUserRole.SUPER_ADMIN)

  # Act
  created_user = auth_service.register(user_data)

  # Verify
  db_user = db_session.query(User).filter_by(email=user_data.email).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid

  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.SUPER_ADMIN.value


def test_duplicate_email_integration_error(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:

  # Arrange: Create user data
  first_user_data = _create_user_data(db_session, faker, EnumUserRole.SUPER_ADMIN)
  second_user_data = first_user_data.model_copy()

  # Act
  auth_service.register(first_user_data)

  # Verify
  db_user = db_session.query(User).filter_by(email=first_user_data.email).first()
  assert db_user is not None

  # Assert
  with pytest.raises(UserAlreadyExistExceptionError, match="A user with this email already exists"):
    auth_service.register(second_user_data)
