from datetime import UTC, datetime, timedelta

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.exception import JwtInvalidTokenError
from api.modules.auth.model import AuthToken
from api.modules.auth.password.service import PasswordService
from api.modules.auth.schema import FormAuthResetPasswordSchema, TokenType
from api.modules.auth.service import AuthService
from api.modules.user.model import User
from utils.hash import hash_token


def _sample_data(db_session: Session, faker: Faker) -> dict:
  session_id = hex(id(db_session))
  return {
    "email": f"test_integration_reset_password_{session_id}_{faker.email()}",
    "new_password": "P@ssW0rd123",
    "confirm_password": "P@ssW0rd123",
    "invalid_password": faker.password(),
    "uuid": faker.uuid4(),
    "family_id": faker.uuid4(),
    "token": faker.uuid4(),
    "invalid_token": faker.uuid4(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
  }


def _create_db_user(data: dict[str, str], hashed_pw: str, db_session: Session) -> User:
  test_user = User(
    email=data["email"],
    password=hashed_pw,
    uuid=data["uuid"],
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
  )
  db_session.add(test_user)
  db_session.commit()

  return test_user


def _create_db_reset_token(
  hashed_token: str, data: dict[str, str], user: User, expires_at: datetime, db_session: Session
) -> AuthToken:
  reset_token = AuthToken(
    token_hash=hashed_token,
    token_type=TokenType.PASSWORD_UPDATE,
    user_id=user.id,
    expires_at=expires_at,
    family_id=data["family_id"],
    is_revoked=False,
  )
  db_session.add(reset_token)
  db_session.commit()

  return reset_token


def test_reset_password_success_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange
  user_data = _sample_data(db_session, faker)
  hashed_pw = PasswordService().password_hash(user_data["new_password"])

  test_user = _create_db_user(user_data, hashed_pw, db_session)

  # We need a token that is signed with the SAME keys as the auth_service
  # The auth_service fixture creates its own JwtService with tmp keys.
  # To get a valid token, we can use the auth_service's internal jwt_service.
  # Since it's not public, we can access it via the attribute.

  jwt_service = auth_service.jwt_service
  token_obj = jwt_service.create_token(
    TokenType.PASSWORD_UPDATE, test_user.uuid, user_data["family_id"]
  )
  token_string = str(token_obj.encoded)

  reset_token = _create_db_reset_token(
    hash_token(token_string),
    user_data,
    test_user,
    expires_at=datetime.now(UTC) + timedelta(hours=1),
    db_session=db_session,
  )

  reset_payload = FormAuthResetPasswordSchema(
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
  assert reset_token.deleted_at is not None


def test_reset_password_invalid_token_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  # Arrange
  user_data = _sample_data(db_session, faker)

  reset_payload = FormAuthResetPasswordSchema(
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
  user_data = _sample_data(db_session, faker)
  hashed_pw = PasswordService().password_hash(user_data["new_password"])

  # Create the user
  test_user = _create_db_user(user_data, hashed_pw, db_session)

  # Generate a real token but set it as expired in the DB
  jwt_service = auth_service.jwt_service
  token_obj = jwt_service.create_token(
    TokenType.PASSWORD_UPDATE, test_user.uuid, user_data["family_id"]
  )
  token_string = str(token_obj.encoded)

  _create_db_reset_token(
    hash_token(token_string),
    user_data,
    test_user,
    expires_at=datetime.now(UTC) - timedelta(hours=1),
    db_session=db_session,
  )

  reset_payload = FormAuthResetPasswordSchema(
    token=token_string,
    new_password=user_data["new_password"],
    confirm_password=user_data["confirm_password"],
  )

  # Act & Assert
  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(reset_payload)
