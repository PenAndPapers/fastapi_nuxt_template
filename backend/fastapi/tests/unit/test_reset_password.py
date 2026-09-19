from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from api.modules.auth.exception import JwtInvalidTokenError
from api.modules.auth.model import Auth
from api.modules.auth.schema import AuthResetPasswordSchema, TokenType
from api.modules.auth.service import AuthService
from api.modules.user.model import User


@pytest.fixture()
def mock_db_session() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_auth_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_device_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_user_role_repo() -> MagicMock:
  return MagicMock()


@pytest.fixture
def mock_jwt_service() -> MagicMock:
  service = MagicMock()
  return service


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
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
  mock_user_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_password_service: MagicMock,
  mock_db_session: MagicMock,
) -> None:
  data = sample_data()
  # Arrange
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC) + timedelta(hours=1),
  )

  mock_auth_repo.get_token_by_hash.return_value = mock_token

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
  mock_jwt_service.decode.return_value = mock_decoded_token

  mock_user = User(id=1, email=data["email"], uuid=data["uuid"])
  mock_user_repo.get_user_by_uuid.return_value = mock_user

  # Set mock token family_id to match
  mock_token.family_id = data["family_id"]

  # Act
  result = auth_service.reset_password(payload)

  # Assert
  assert result is True
  mock_user_repo.update_password.assert_called_once()
  mock_auth_repo.revoke_user_active_tokens.assert_called_once_with(
    mock_user.id, TokenType.PASSWORD_UPDATE
  )
  mock_db_session.commit.assert_called_once()


def test_reset_password_invalid_token(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["invalid_token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_auth_repo.get_token_by_hash.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)


def test_reset_password_expired_token(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC) - timedelta(hours=1),
  )
  mock_auth_repo.get_token_by_hash.return_value = mock_token

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)


def test_reset_password_wrong_token_type(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.ACCESS,
    expires_at=datetime.now(UTC),
  )
  mock_auth_repo.get_token_by_hash.return_value = mock_token

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)


def test_reset_password_decode_failed(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
  mock_jwt_service: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  mock_auth_repo.get_token_by_hash.return_value = mock_token
  mock_jwt_service.decode.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)


def test_reset_password_user_not_found(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  mock_auth_repo.get_token_by_hash.return_value = mock_token
  mock_jwt_service.decode.return_value = {"sub": "nonexistent_uuid"}
  mock_user_repo.get_user_by_uuid.return_value = None

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)


def test_reset_password_mismatch_attributes(
  auth_service: AuthService,
  mock_auth_repo: MagicMock,
  mock_jwt_service: MagicMock,
  mock_user_repo: MagicMock,
) -> None:
  data = sample_data()
  payload = AuthResetPasswordSchema(
    token=data["token"],
    new_password=data["new_password"],
    confirm_password=data["confirm_password"],
  )

  mock_token = Auth(
    id=1,
    token_hash=data["token"],
    token_type=TokenType.PASSWORD_UPDATE,
    expires_at=datetime.now(UTC),
  )
  mock_auth_repo.get_token_by_hash.return_value = mock_token

  mock_decoded_token = {
    "sub": "wrong_uuid",
    "family_id": "wrong_family",
    "exp": (datetime.now()).timestamp(),
  }
  mock_jwt_service.decode.return_value = mock_decoded_token
  mock_user = User(id=1, email=data["email"], uuid=data["uuid"])
  mock_user_repo.get_user_by_uuid.return_value = mock_user

  with pytest.raises(JwtInvalidTokenError):
    auth_service.reset_password(payload)
