from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from api.modules.auth.exception import JwtExpiredError, JwtInvalidTokenError
from api.modules.auth.jwt.service import JwtService
from api.modules.auth.schema import JwtPayload, TokenType


@pytest.fixture
def mock_settings() -> MagicMock:
  """Mock settings to avoid reading from actual files during unit tests."""
  with patch("api.modules.auth.jwt.service.settings") as mock:
    mock.jwt_algorithm = "ES256"
    mock.jwt_issuer = "test-issuer"
    mock.jwt_audience = "test-audience"
    mock.access_token_expire_minutes = 15
    mock.refresh_token_expire_days = 7
    mock.email_verification_token_expire_days = 7
    mock.password_reset_token_expire_minutes = 15

    # Mock Path.read_text() for keys
    mock.private_key_path = MagicMock()
    mock.private_key_path.read_text.return_value = "mock-private-key"
    mock.public_key_path = MagicMock()
    mock.public_key_path.read_text.return_value = "mock-public-key"

    yield mock


@pytest.fixture
def jwt_service(mock_settings: MagicMock) -> JwtService:
  return JwtService()


@pytest.fixture
def sample_payload() -> JwtPayload:
  return JwtPayload(
    token_type=TokenType.ACCESS,
    exp=int((datetime.now() + timedelta(minutes=15)).timestamp()),
    nbf=int(datetime.now().timestamp()),
    iat=int(datetime.now().timestamp()),
    iss="test-issuer",
    aud="test-audience",
    sub=str(uuid4()),
    jti=str(uuid4()),
    family_id=str(uuid4()),
  )


def test_get_token_jti(jwt_service: JwtService) -> None:
  jti = jwt_service.get_token_jti()
  assert isinstance(jti, str)
  assert len(jti) > 0


def test_get_token_type_expiration(jwt_service: JwtService) -> None:
  assert jwt_service.get_token_type_expiration(TokenType.ACCESS) == 15 * 60
  assert jwt_service.get_token_type_expiration(TokenType.REFRESH) == 7 * 24 * 60 * 60
  assert jwt_service.get_token_type_expiration(TokenType.CONFIRM_EMAIL) == 7 * 24 * 60 * 60
  assert jwt_service.get_token_type_expiration(TokenType.PASSWORD_UPDATE) == 15 * 60

  with pytest.raises(ValueError, match="Unknown token type"):
    jwt_service.get_token_type_expiration("invalid_type")  # type: ignore


def test_get_default_jwt_claims(jwt_service: JwtService) -> None:
  claims = jwt_service.get_default_jwt_claims(TokenType.ACCESS)

  assert claims["iss"] == "test-issuer"
  assert claims["aud"] == "test-audience"
  assert "iat" in claims
  assert "nbf" in claims
  assert "exp" in claims

  # Verify exp is roughly 15 mins from now
  expected_exp = int(datetime.now().timestamp() + 15 * 60)
  assert abs(claims["exp"] - expected_exp) < 5


def test_encode_decode_success(jwt_service: JwtService, sample_payload: JwtPayload) -> None:
  # We must mock jwt.encode and jwt.decode because we are using mock keys
  with patch("jwt.encode") as mock_encode, patch("jwt.decode") as mock_decode:
    mock_encode.return_value = "mocked.jwt.token"
    mock_decode.return_value = sample_payload.model_dump()

    token = jwt_service.encode(sample_payload)
    assert token == "mocked.jwt.token"  # noqa S105
    mock_encode.assert_called_once()

    decoded = jwt_service.decode(token)
    assert decoded == sample_payload.model_dump()
    mock_decode.assert_called_once_with(
      "mocked.jwt.token", "mock-public-key", algorithms=["ES256"], audience=None, issuer=None
    )


def test_decode_expired_token(jwt_service: JwtService) -> None:
  with patch("jwt.decode") as mock_decode:
    import jwt as jwt_lib

    mock_decode.side_effect = jwt_lib.ExpiredSignatureError("Expired")

    with pytest.raises(JwtExpiredError, match="JWT expired"):
      jwt_service.decode("expired.token")


def test_decode_invalid_token(jwt_service: JwtService) -> None:
  with patch("jwt.decode") as mock_decode:
    import jwt as jwt_lib

    mock_decode.side_effect = jwt_lib.InvalidTokenError("Invalid")

    with pytest.raises(JwtInvalidTokenError, match="JWT invalid token"):
      jwt_service.decode("invalid.token")
