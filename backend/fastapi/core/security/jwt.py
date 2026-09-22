from datetime import UTC, datetime
from uuid import uuid4

import jwt

from core.config import Settings
from core.exception import JwtExpiredError, JwtInvalidTokenError
from core.schema import GeneratedTokenFormSchema, JwtFormSchema, TokenType

settings = Settings()


algorithm = settings.jwt_algorithm
private_key = settings.private_key_path.read_text()
public_key = settings.public_key_path.read_text()

jwt_issuer = settings.jwt_issuer
jwt_audience = settings.jwt_audience
jwt_expiration_seconds = settings.access_token_expire_minutes * 60
jwt_refresh_expiration_seconds = settings.refresh_token_expire_days * 24 * 60 * 60
jwt_confirm_email_expiration_seconds = settings.email_verification_token_expire_days * 24 * 60 * 60
jwt_password_update_expiration_seconds = settings.password_reset_token_expire_minutes * 60


def get_token_jti() -> str:
  """Get the unique token identifier (JTI) from a JWT token.

  Returns:
      str: A new uuid string.
  """
  return str(uuid4())


def get_token_type_expiration(token_type: TokenType) -> int:
  """Get the expiration time in seconds for a given token type.

  Args:
      token_type: The type of token for which to get the expiration.

  Returns:
      int: The expiration time in seconds.
  """
  match token_type:
    case TokenType.ACCESS:
      return jwt_expiration_seconds
    case TokenType.REFRESH:
      return jwt_refresh_expiration_seconds
    case TokenType.CONFIRM_EMAIL:
      return jwt_confirm_email_expiration_seconds
    case TokenType.PASSWORD_UPDATE:
      return jwt_password_update_expiration_seconds
    case _:
      raise ValueError(f"Unknown token type: {token_type}")


def get_default_jwt_claims(token_type: TokenType) -> dict:
  """Get default JWT claims for a new token.

  Args:
      token_type: The type of token for which to get the claims.

  Returns:
      dict: Default claims payload.
  """

  return {
    "iss": jwt_issuer,
    "aud": jwt_audience,
    "iat": int(datetime.now(UTC).timestamp()),
    "nbf": int(datetime.now(UTC).timestamp()),
    "exp": int(datetime.now(UTC).timestamp() + get_token_type_expiration(token_type)),
  }


def jwt_encode(payload: JwtFormSchema) -> str:
  """Encode a payload dictionary or model into a signed JWT string.

  Args:
      payload: Claims data to include in the token payload.

  Returns:
      str: Signed JWT string.
  """
  return jwt.encode(payload.model_dump(mode="json"), private_key, algorithm=algorithm)


def jwt_decode(token: str, audience: str | None = None, issuer: str | None = None) -> JwtFormSchema:
  """Decode and verify a signed JWT string using the public key.

  Args:
      token: The raw JWT string to verify and decode.
      audience: Optional intended audience for the token.
      issuer: Optional issuer of the token.

  Returns:
      JwtFormSchema: The decoded token claims payload.

  Raises:
      JwtExpiredError: If the token's `exp` claim is in the past.
      JwtInvalidTokenError: If signature verification fails or token is malformed.
  """
  try:
    decoded_token = jwt.decode(
      token, public_key, algorithms=[algorithm], audience=audience, issuer=issuer
    )

    return JwtFormSchema.model_validate(decoded_token, from_attributes=True)
  except jwt.ExpiredSignatureError as e:
    raise JwtExpiredError("JWT expired") from e
  except jwt.InvalidTokenError as e:
    # Catch-all for malformed signatures, incorrect algorithms, or bad structures
    raise JwtInvalidTokenError("JWT invalid token") from e


def create_token(token_type: TokenType, sub: str, family_id: str) -> GeneratedTokenFormSchema:
  """Create a new JWT token.

  Args:
      token_type: The type of token to create.
      sub: The subject identifier of the token.
      family_id: The family identifier of the token family.

  Returns:
      tuple[str, int]: The created token and expiration time in seconds.
  """

  claims = get_default_jwt_claims(token_type)
  claims.update(
    {
      "token_type": token_type.value,
      "sub": sub,
      "family_id": family_id,
      "jti": get_token_jti(),
    }
  )

  encoded = jwt_encode(JwtFormSchema(**claims))

  return GeneratedTokenFormSchema(
    encoded=str(encoded), exp=claims["exp"], family_id=claims["family_id"]
  )
