from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.exception import JwtInvalidTokenError
from api.modules.auth.jwt.service import JwtService
from api.modules.auth.model import Auth
from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository, DeviceRepository
from api.modules.auth.schema import AuthResetPasswordSchema, TokenType
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


def sample_user_data(db_session: Session, faker: Faker) -> dict:
  password = faker.password()
  return {
    "email": faker.email(),
    "new_password": password,
    "confirm_password": password,
    "invalid_password": faker.password(),
    "uuid": faker.uuid4(),
    "family_id": faker.uuid4(),
    "token": faker.uuid4(),
    "invalid_token": faker.uuid4(),
  }


def test_reset_password_success_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange
  user_data = sample_user_data(db_session, faker)
  hashed_pw = PasswordService().password_hash(user_data["new_password"])
  test_user = User(
    email=user_data["email"],
    password=hashed_pw,
    uuid=user_data["uuid"],
  )
  db_session.add(test_user)
  db_session.commit()

  # We need a token that is signed with the SAME keys as the auth_service
  # The auth_service fixture creates its own JwtService with tmp keys.
  # To get a valid token, we can use the auth_service's internal jwt_service.
  # Since it's not public, we can access it via the attribute.

  jwt_service = auth_service.jwt_service
  token_obj = jwt_service.create_token(
    TokenType.PASSWORD_UPDATE, test_user.uuid, user_data["family_id"]
  )
  token_string = str(token_obj.encoded)

  reset_token = Auth(
    token_hash=token_string,
    token_type=TokenType.PASSWORD_UPDATE,
    user_id=test_user.id,
    expires_at=datetime.now() + timedelta(hours=1),
    family_id="family_123",
    is_revoked=False,
  )
  db_session.add(reset_token)
  db_session.commit()

  reset_payload = AuthResetPasswordSchema(
    token=token_string,
    new_password=user_data["new_password"],
    confirm_password=user_data["confirm_password"],
  )

  # Act
  result = auth_service.reset_password(reset_payload)

  # Assert
  assert result is True

  updated_user = db_session.query(User).filter_by(id=test_user.id).first()
  assert PasswordService().verify_password(user_data["new_password"], updated_user.password)

  assert reset_token.is_revoked is True


def test_reset_password_invalid_token_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange
  user_data = sample_user_data(db_session, faker)

  reset_payload = AuthResetPasswordSchema(
    token=user_data["invalid_token"],
    new_password=user_data["new_password"],
    confirm_password=user_data["confirm_password"],
  )

  # Act & Assert
  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(reset_payload)


def test_reset_password_expired_token_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange
  user_data = sample_user_data(db_session, faker)
  test_user = User(
    email=user_data["email"],
    password=PasswordService().password_hash(user_data["new_password"]),
    uuid=user_data["uuid"],
  )
  db_session.add(test_user)
  db_session.commit()

  # Generate a real token but set it as expired in the DB
  jwt_service = auth_service.jwt_service
  token_obj = jwt_service.create_token(
    TokenType.PASSWORD_UPDATE, test_user.uuid, user_data["family_id"]
  )
  token_string = str(token_obj.encoded)

  reset_token = Auth(
    token_hash=token_string,
    token_type=TokenType.PASSWORD_UPDATE,
    user_id=test_user.id,
    expires_at=datetime.now() - timedelta(hours=1),
    family_id=user_data["family_id"],
    is_revoked=False,
  )
  db_session.add(reset_token)
  db_session.commit()

  reset_payload = AuthResetPasswordSchema(
    token=token_string,
    new_password=user_data["new_password"],
    confirm_password=user_data["confirm_password"],
  )

  # Act & Assert
  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(reset_payload)
