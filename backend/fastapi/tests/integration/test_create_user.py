import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.jwt.service import JwtService
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository
from api.modules.auth.service import AuthService
from api.modules.user.model import Role, User, UserRole
from api.modules.user.repository import UserRepository, UserRoleRepository
from api.modules.user.schema import EnumUserRole, UserCreateSchema


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
  # Initialize real repositories and services with the test DB session
  auth_repo = AuthRepository(db_session)
  user_repo = UserRepository(db_session)
  user_role_repo = UserRoleRepository(db_session)
  jwt_service = JwtService()
  password_service = PasswordService()

  return AuthService(
    repository=auth_repo,
    user_repository=user_repo,
    user_role_repository=user_role_repo,
    jwt_service=jwt_service,
    password_service=password_service,
  )


def test_create_user_integration_success(
  auth_service: AuthService, db_session: Session, random_string: str, faker: Faker
) -> None:
  # Arrange: Ensure the role exists in DB
  role_name = EnumUserRole.USER.value
  role = db_session.query(Role).filter_by(name=role_name).first()
  if not role:
    role = Role(name=role_name, description="Test User Role")
    db_session.add(role)
    db_session.commit()

  email = f"{random_string}_{faker.email()}"
  password = faker.password()

  user_data = UserCreateSchema(
    email=email,
    password=password,
    first_name=f"{faker.first_name()}",
    last_name=f"{faker.last_name()}",
    address=f"{faker.address()}",
    phone_number=f"{faker.phone_number()}",
    role=EnumUserRole.USER,
  )

  # Act
  created_user = auth_service.create_user(user_data)

  # Assert
  # 1. Verify user exists in database
  db_user = db_session.query(User).filter_by(email=email).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid
  assert db_user.password != password

  # Verify role association exists in junction table
  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.USER.value


def test_create_superadmin_integration_success(
  auth_service: AuthService, db_session: Session, random_string: str, faker: Faker
) -> None:
  # Arrange: Ensure the role exists in DB
  role_name = EnumUserRole.SUPER_ADMIN.value
  role = db_session.query(Role).filter_by(name=role_name).first()
  if not role:
    role = Role(name=role_name, description="Test Superadmin Role")
    db_session.add(role)
    db_session.commit()

  email = f"{random_string}_{faker.email()}"
  password = faker.password()

  user_data = UserCreateSchema(
    email=email,
    password=password,
    first_name=f"{faker.first_name()}",
    last_name=f"{faker.last_name()}",
    address=f"{faker.address()}",
    phone_number=f"{faker.phone_number()}",
    role=EnumUserRole.SUPER_ADMIN,
  )

  # Act
  created_user = auth_service.create_user(user_data)

  # Verify
  db_user = db_session.query(User).filter_by(email=email).first()
  assert db_user is not None
  assert db_user.id == created_user.id
  assert db_user.uuid == created_user.uuid
  assert db_user.password != password

  user_role = db_session.query(UserRole).filter_by(user_id=db_user.id).first()
  assert user_role is not None

  db_role = db_session.query(Role).filter_by(id=user_role.role_id).first()
  assert db_role.name == EnumUserRole.SUPER_ADMIN.value
