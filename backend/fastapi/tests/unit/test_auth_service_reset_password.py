from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from api.modules.auth.exception import JwtInvalidTokenError
from api.modules.auth.model import AuthToken
from api.modules.auth.schema import FormAuthResetPasswordSchema, TokenType
from api.modules.auth.service import AuthService
from api.modules.user.model import User


def sample_data() -> dict:
  return {
    "token": "valid_token_hash",
    "invalid_token": "Inv@lid_Token_hash",
    "new_password": "New_P@ssword_123",
    "confirm_password": "New_P@ssword_123",
    "uuid": "user-uuid-123",
    "email": "test@example.com",
    "iss": "http://localhost:8000",
    "aud": "http://localhost:3000",
    "sub": "user-uuid-123",
    "jti": "token-jti-123",
    "family_id": "family_123",
  }


def test_reset_password_success(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
  unit_mock_user_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_password_service: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC) + timedelta(hours=1),
  )

  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token

  # Mock JWT decode
  mock_decoded_token = {
    "token_type": TokenType.PASSWORD_UPDATE,
    "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
    "nbf": int(datetime.now(UTC).timestamp()),
    "iat": int(datetime.now(UTC).timestamp()),
    "iss": data["iss"],
    "aud": data["aud"],
    "sub": data["sub"],
    "jti": data["jti"],
    "family_id": data["family_id"],
  }
  unit_mock_jwt_service.decode.return_value = mock_decoded_token

  mock_user = User(id=1, email=data["email"], uuid=data["uuid"])
  unit_mock_user_repo.get_user_by_uuid.return_value = mock_user

  # Set mock token family_id to match
  mock_token.family_id = data["family_id"]

  # Act
  result = unit_mock_auth_service.reset_password(payload)

  # Assert
  assert result is True
  unit_mock_user_repo.update_password.assert_called_once()
  unit_mock_auth_repo.revoke_user_active_tokens.assert_called_once_with(
    mock_user.id, TokenType.PASSWORD_UPDATE
  )


def test_reset_password_invalid_token(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["invalid_token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  unit_mock_auth_repo.get_token_by_hash.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)


def test_reset_password_expired_token(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC) - timedelta(hours=1),
  )
  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)


def test_reset_password_wrong_token_type(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.ACCESS,
    expires_at=datetime.now(UTC),
  )
  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)


def test_reset_password_decode_failed(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token
  unit_mock_jwt_service.decode.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)


def test_reset_password_user_not_found(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token
  unit_mock_jwt_service.decode.return_value = {"sub": "nonexistent_uuid"}
  unit_mock_user_repo.get_user_by_uuid.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)


def test_reset_password_mismatch_attributes(
  unit_mock_auth_service: AuthService,
  unit_mock_auth_repo: MagicMock,
  unit_mock_jwt_service: MagicMock,
  unit_mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = FormAuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = AuthToken(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  unit_mock_auth_repo.get_token_by_hash.return_value = mock_token

  mock_decoded_token = {
    "sub": "wrong_uuid",
    "family_id": "wrong_family",
    "exp": (datetime.now(UTC)).timestamp(),
  }
  unit_mock_jwt_service.decode.return_value = mock_decoded_token
  mock_user = User(id=1, email=data["email"], uuid=data["uuid"])
  unit_mock_user_repo.get_user_by_uuid.return_value = mock_user

  with pytest.raises(JwtInvalidTokenError):
    unit_mock_auth_service.reset_password(payload)
