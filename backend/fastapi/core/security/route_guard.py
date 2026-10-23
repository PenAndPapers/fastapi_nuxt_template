import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from api.modules.auth.model import AuthToken
from api.modules.user.model import User
from core.config import get_settings
from core.database import DatabaseDep
from core.schema import TokenType
from utils.hash import hash_token

from .jwt import jwt_decode

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer()


settings = get_settings()


def _raise_unauthorized(
  internal_log_msg: str, user_detail: str = "Invalid authentication credentials"
) -> None:
  """
  Helper to log internal security warnings and raise standardized HTTP 401 exceptions.

  Args:
      internal_log_msg: The internal log message to record.
      user_detail: The user-facing detail message to include in the HTTP response.
  """
  logger.warning(internal_log_msg)
  raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=user_detail,
    headers={"WWW-Authenticate": "Bearer"},
  )


def _get_current_user(
  db: DatabaseDep, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]
) -> User:
  """
  Validate authentication token and return user object.

  Args:
      db: The database session.
      credentials: The HTTP authorization credentials from the request.

  Returns:
      User: The user object if the token is valid, otherwise raises an HTTP 401 exception with a user-facing detail.
  """
  token = credentials.credentials

  try:
    decoded_token = jwt_decode(token, audience=settings.jwt_audience, issuer=settings.jwt_issuer)
  except Exception as e:
    _raise_unauthorized(f"JWT decode failed: {e}", "Token is invalid")

  if decoded_token.token_type != TokenType.ACCESS.value:
    _raise_unauthorized(
      f"Invalid token type provided: {decoded_token.token_type}", "Token is invalid"
    )

  # TODO: Add filter by is_verified=True later so that only verified users can access protected routes
  db_user = db.query(User).filter_by(uuid=decoded_token.sub).first()

  if not db_user:
    _raise_unauthorized(f"User not found for sub: {decoded_token.sub}", "Token is invalid")

  query = select(AuthToken).filter(
    AuthToken.token_hash == hash_token(token),
    AuthToken.token_type == decoded_token.token_type,
    AuthToken.user_id == db_user.id,
    AuthToken.is_revoked == False,  # noqa: E712
  )
  db_token = db.execute(query).scalar_one_or_none()

  if not db_token:
    _raise_unauthorized(
      f"Token revoked or missing in DB for user_uuid: {db_user.uuid}", "Token is revoked or invalid"
    )

  token_expires_at = (
    db_token.expires_at if db_token.expires_at.tzinfo else db_token.expires_at.replace(tzinfo=UTC)
  )

  if token_expires_at < datetime.now(UTC) or db_token.token_type != TokenType.ACCESS.value:
    _raise_unauthorized(
      f"Token expired or type mismatch in DB for user_uuid: {db_user.uuid}",
      "Token has expired or type mismatch",
    )

  return db_user


RouteGuardDep = Annotated[User, Depends(_get_current_user), "Route Guard"]
