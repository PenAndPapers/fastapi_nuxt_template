import jwt

from core.config import Settings

from ..exception import JwtExpiredError, JwtInvalidTokenError
from ..schema import JwtPayload

# Load RSA/ECDSA keys at module startup for fast token validation
# Note: Ensure these paths exist or are injected via environment/secrets manager
PRIVATE_KEY = open("/app/certs/private_key.pem").read()
PUBLIC_KEY = open("/app/certs/public_key.pem").read()

settings = Settings()


class JwtService:
  """Handles encoding and decoding of JSON Web Tokens (JWT) using asymmetric cryptography."""

  def __init__(self) -> None:
    # ES256 (ECDSA using P-256 and SHA-256) requires public/private key pairs
    self._algorithm = settings.jwt_algorithm
    self._private_key = settings.private_key_path.read_text()
    self._public_key = settings.public_key_path.read_text()

  def encode(self, payload: JwtPayload) -> str:
    """Encode a payload dictionary or model into a signed JWT string.

    Args:
        payload: Claims data to include in the token payload.

    Returns:
        str: Signed JWT string.
    """
    return jwt.encode(payload, self._private_key, algorithm=self._algorithm)

  def decode(self, token: str) -> dict:
    """Decode and verify a signed JWT string using the public key.

    Args:
        token: The raw JWT string to verify and decode.

    Returns:
        dict: The decoded token claims payload.

    Raises:
        JwtExpiredError: If the token's `exp` claim is in the past.
        JwtInvalidTokenError: If signature verification fails or token is malformed.
    """
    try:
      return jwt.decode(token, self._public_key, algorithms=[self.algorithm])
    except jwt.ExpiredError as e:
      raise JwtExpiredError("JWT expired") from e
    except jwt.InvalidTokenError as e:
      # Catch-all for malformed signatures, incorrect algorithms, or bad structures
      raise JwtInvalidTokenError("JWT invalid token") from e
