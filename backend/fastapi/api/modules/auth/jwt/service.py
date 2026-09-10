from datetime import datetime
from uuid import uuid4

import jwt

from core.config import Settings

from ..exception import JwtExpiredError, JwtInvalidTokenError
from ..schema import JwtPayload, TokenType

settings = Settings()


class JwtService:
  """Handles encoding and decoding of JSON Web Tokens (JWT) using asymmetric cryptography."""

  def __init__(self) -> None:
    # ES256 (ECDSA using P-256 and SHA-256) requires public/private key pairs
    self._algorithm = settings.jwt_algorithm
    self._private_key = settings.private_key_path.read_text()
    self._public_key = settings.public_key_path.read_text()

    self._jwt_issuer = settings.jwt_issuer
    self._jwt_audience = settings.jwt_audience
    self._jwt_expiration_seconds = settings.access_token_expire_minutes * 60
    self._jwt_refresh_expiration_seconds = settings.refresh_token_expire_days * 24 * 60 * 60
    self._jwt_confirm_email_expiration_seconds = (
      settings.email_verification_token_expire_days * 24 * 60 * 60
    )
    self._jwt_password_update_expiration_seconds = settings.password_reset_token_expire_minutes * 60

  def get_token_jti(self) -> str:
    """Get the unique token identifier (JTI) from a JWT token.

    Returns:
        str: A new uuid string.
    """
    return str(uuid4())

  def get_token_type_expiration(self, token_type: TokenType) -> int:
    """Get the expiration time in seconds for a given token type.

    Args:
        token_type: The type of token for which to get the expiration.

    Returns:
        int: The expiration time in seconds.
    """
    match token_type:
      case TokenType.ACCESS:
        return self._jwt_expiration_seconds
      case TokenType.REFRESH:
        return self._jwt_refresh_expiration_seconds
      case TokenType.CONFIRM_EMAIL:
        return self._jwt_confirm_email_expiration_seconds
      case TokenType.PASSWORD_UPDATE:
        return self._jwt_password_update_expiration_seconds
      case _:
        raise ValueError(f"Unknown token type: {token_type}")

  def get_default_jwt_claims(self, token_type: TokenType) -> dict:
    """Get default JWT claims for a new token.

    Args:
        token_type: The type of token for which to get the claims.

    Returns:
        dict: Default claims payload.
    """

    return {
      "iss": self._jwt_issuer,
      "aud": self._jwt_audience,
      "iat": int(datetime.now().timestamp()),
      "nbf": int(datetime.now().timestamp()),
      "exp": int(datetime.now().timestamp() + self.get_token_type_expiration(token_type)),
    }

  def encode(self, payload: JwtPayload) -> str:
    """Encode a payload dictionary or model into a signed JWT string.

    Args:
        payload: Claims data to include in the token payload.

    Returns:
        str: Signed JWT string.
    """
    return jwt.encode(payload.model_dump(mode="json"), self._private_key, algorithm=self._algorithm)

  def decode(self, token: str, audience: str | None = None, issuer: str | None = None) -> dict:
    """Decode and verify a signed JWT string using the public key.

    Args:
        token: The raw JWT string to verify and decode.
        audience: Optional intended audience for the token.
        issuer: Optional issuer of the token.

    Returns:
        dict: The decoded token claims payload.

    Raises:
        JwtExpiredError: If the token's `exp` claim is in the past.
        JwtInvalidTokenError: If signature verification fails or token is malformed.
    """
    try:
      return jwt.decode(
        token, self._public_key, algorithms=[self._algorithm], audience=audience, issuer=issuer
      )
    except jwt.ExpiredSignatureError as e:
      raise JwtExpiredError("JWT expired") from e
    except jwt.InvalidTokenError as e:
      # Catch-all for malformed signatures, incorrect algorithms, or bad structures
      raise JwtInvalidTokenError("JWT invalid token") from e
