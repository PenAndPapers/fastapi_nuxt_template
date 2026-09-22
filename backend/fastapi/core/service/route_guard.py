# ---- Route Guard service ----
# TODO: Implement route guard service
# - Check if user is authenticated using JWT token
# - Check if JWT token has valid signature and is not expired
# - Check JWT token against DB token properties to ensure it matches (user_id, is_revoked, expires_at, family_id)
#
#
# We build our own repository helper methods here instead of using other service classes
# because we want to keep the service classes focused on their primary responsibilities.
# This way, we can easily test the service classes independently and maintain a clean codebase.
# ---- Route Guard ----
import logging
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.modules.auth.model import AuthToken
from api.modules.user.model import User
from core.database import DatabaseDep

security_scheme = HTTPBearer()
database = DatabaseDep()
logger = logging.getLogger(__name__)


def auth_creds() -> HTTPAuthorizationCredentials:
  return HTTPAuthorizationCredentials(Depends(security_scheme))


def _get_db_current_user(uuid: str) -> User:
  """
  Get current user from request headers.
  """

  # TODO: Add filter by is_verified=True
  user = database.query(User).filter_by(uuid=uuid).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

  return user


def _get_db_auth_token(hashed_token: str, user_id: int) -> AuthToken:
  """
  Get authentication token from request headers.
  """
  token = (
    database.query(AuthToken)
    .filter_by(token_hash=hashed_token, is_revoked=False, user_id=user_id)
    .first()
  )
  if not token:
    logger.error("Token not found, revoked or expired")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")

  if token and token.expires_at < datetime.now(UTC):
    logger.error("Token expired")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

  return token


def _validate_auth_token() -> None:
  """
  Validate authentication token.
  """
  pass


class RouteGuardService:
  def __init__(self) -> None:
    pass
