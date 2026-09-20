from pathlib import Path
from unittest.mock import patch

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.jwt.service import JwtService
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository, DeviceRepository
from api.modules.auth.schema import FormAuthForgetPasswordSchema, FormDeviceSchema, TokenType
from api.modules.auth.service import AuthService
from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository


@pytest.fixture
def auth_service(
  db_session: Session, tmp_path: Path, private_key_fixture: str, public_key_fixture: str
) -> AuthService:
  priv_file = tmp_path / "private_key.pem"
  pub_file = tmp_path / "public_key.pem"
  priv_file.write_text(private_key_fixture)
  pub_file.write_text(public_key_fixture)

  from api.modules.auth.jwt.service import settings

  with (
    patch.object(settings, "private_key_path", priv_file),
    patch.object(settings, "public_key_path", pub_file),
  ):
    jwt_service = JwtService()

    return AuthService(
      db=db_session,
      repository=AuthRepository(db_session),
      device_repository=DeviceRepository(db_session),
      user_repository=UserRepository(db_session),
      user_role_repository=UserRoleRepository(db_session),
      jwt_service=jwt_service,
      password_service=PasswordService(),
    )


def sample_device_data(
  db_session: Session, faker: Faker
) -> dict[str, str | float | int | FormDeviceSchema]:
  session_id = hex(id(db_session))

  return {
    "email": f"test_integration_forgot_password_{session_id}_{faker.email()}",
    "password": faker.password(),
    "uuid": faker.uuid4(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
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


def test_forget_password_success_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_device_data(db_session, faker)
  # Arrange: Create user in DB
  hashed_pw = PasswordService().password_hash(data["password"])
  test_user = User(
    email=data["email"],
    password=hashed_pw,
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    uuid=data["uuid"],
  )
  db_session.add(test_user)
  db_session.commit()

  forget_data = FormAuthForgetPasswordSchema(email=data["email"], device=data["device"])

  # Act
  result = auth_service.forget_password(forget_data)

  # Assert
  assert result is True
  # Check if token was stored in DB (we can check via repository or query)
  from api.modules.auth.repository import AuthRepository

  AuthRepository(db_session)
  # Since we don't have a get_token method, we check if any token exists for this user
  from api.modules.auth.model import AuthToken

  token = db_session.query(AuthToken).filter_by(user_id=test_user.id).first()
  assert token is not None
  assert token.token_type == TokenType.PASSWORD_UPDATE.value


def test_forget_password_user_not_found_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = sample_device_data(db_session, faker)
  # Use a different email that isn't in the DB
  forget_data = FormAuthForgetPasswordSchema(
    email=f"nonexistent_{faker.email()}", device=data["device"]
  )

  # Act
  result = auth_service.forget_password(forget_data)

  # Assert
  assert result is True  # Security: return true even if user not found
