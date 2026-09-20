import logging
from datetime import UTC, datetime

from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository
from core.config import get_settings
from core.database import DatabaseDep
from utils.hash import hash_token

from .exception import InvalidCredentialsError, JwtInvalidTokenError
from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository, DeviceRepository
from .schema import (
  FormAuthForgetPasswordSchema,
  FormAuthLoginSchema,
  FormAuthRegisterSchema,
  FormAuthResetPasswordSchema,
  FormDeviceSchema,
  JwtFormSchema,
  SessionTokenResponseSchema,
  TokenFormSchema,
  TokenType,
)

logger = logging.getLogger(__name__)

settings = get_settings()


class AuthService:
  def __init__(
    self,
    db: DatabaseDep,
    repository: AuthRepository,
    device_repository: DeviceRepository,
    user_repository: UserRepository,
    user_role_repository: UserRoleRepository,
    jwt_service: JwtService,
    password_service: PasswordService,
  ) -> None:
    self.db = db
    self.repository = repository
    self.device_repository = device_repository
    self.user_repository = user_repository
    self.user_role_repository = user_role_repository
    self.jwt_service = jwt_service
    self.password_service = password_service

  def register(self, user: FormAuthRegisterSchema) -> User:
    # TODO:
    # - rate limiting.
    # - sending verification emails.

    # Hash password
    user.password = self.password_service.password_hash(user.password)

    # remove role from user so it matches user table schema
    role = user.role
    del user.role

    # Create user repository with access to database
    db_user = self.user_repository.create_user(user)

    # Assign role to user
    self.user_role_repository.assign_role(db_user.id, role)

    return db_user

  def login(self, user: FormAuthLoginSchema) -> SessionTokenResponseSchema:
    # TODO:
    # - store token in database.
    # - rate limiting.
    # - send OTP if first time login within 24 hours via email.

    db_user = self.user_repository.get_user_by_email(user.email)

    if not db_user:
      raise InvalidCredentialsError("Incorrect email or password")

    password_valid = self.password_service.verify_password(user.password, db_user.password)

    if not password_valid:
      raise InvalidCredentialsError("Incorrect email or password")

    family_id = self.jwt_service.get_token_jti()

    access_token = self.jwt_service.create_token(TokenType.ACCESS, db_user.uuid, family_id)
    refresh_token = self.jwt_service.create_token(TokenType.REFRESH, db_user.uuid, family_id)

    return SessionTokenResponseSchema(
      access_token=str(access_token.encoded),
      access_exp=access_token.exp,
      refresh_token=str(refresh_token.encoded),
      refresh_exp=refresh_token.exp,
    )

  def forget_password(self, user: FormAuthForgetPasswordSchema) -> bool:
    # TODO:
    # - rate limiting.
    # - send password reset link to user's email.

    email = user.email
    device = user.device

    db_user = self.user_repository.get_user_by_email(email)

    # Let frontned show message to check the email password update link
    # even if user does not exist
    if not db_user:
      return True

    forget_password_token = self.jwt_service.create_token(
      TokenType.PASSWORD_UPDATE, db_user.uuid, self.jwt_service.get_token_jti()
    )
    # Hash token before storing in database
    # This is done to prevent token leakage in case of database breach
    # or if the database is compromised
    forget_password_token_hash = hash_token(str(forget_password_token.encoded))

    logger.warning(f"forget_password_token: {forget_password_token.encoded}")
    logger.warning(f"forget_password_token_hash: {forget_password_token_hash}")

    device_to_store = FormDeviceSchema(
      client_device_id=device.client_device_id,
      device_type=device.device_type,
      os=device.os,
      browser=device.browser,
      ip_address=device.ip_address,
      latitude=device.latitude,
      longitude=device.longitude,
    )

    # Store device token in database
    db_device = self.device_repository.store_device(
      device_to_store,
      user_id=db_user.id,
    )
    self.db.flush()

    token_to_store = TokenFormSchema(
      token_hash=forget_password_token_hash,
      token_type=TokenType.PASSWORD_UPDATE,
      expires_at=forget_password_token.exp,
      family_id=forget_password_token.family_id,
      is_revoked=False,
      user_id=db_user.id,
      device_id=db_device.id,
    )

    # Store token in database
    self.repository.store_token(token_to_store)

    # Single transaction for all operations
    try:
      self.db.commit()
      return True
    except Exception as e:
      self.db.rollback()
      raise e

  def reset_password(self, payload: FormAuthResetPasswordSchema) -> bool:
    # TODO:
    # - rate limiting for IP and account based
    # - send password reset success message to user's email.

    # Verify password reset token by decoding it
    decoded_token = self.jwt_service.decode(
      payload.token, audience=settings.jwt_audience, issuer=settings.jwt_issuer
    )

    if not decoded_token:
      logger.error(f"Unable to decode token - {payload.token}")
      raise JwtInvalidTokenError("Token is invalid or expired")

    # Verify token hash exists in database
    token_hash = hash_token(str(payload.token))
    db_token = self.repository.get_token_by_hash(token_hash)

    if (
      not db_token
      or db_token.is_revoked
      or (
        db_token.expires_at
        and (
          db_token.expires_at
          if db_token.expires_at.tzinfo
          else db_token.expires_at.replace(tzinfo=UTC)
        )
        < datetime.now(UTC)
      )
      or db_token.token_type != TokenType.PASSWORD_UPDATE
    ):
      logger.error(
        f"\nToken does not exist, revoked, expired or not a password update token - {payload.token}\n"
      )
      raise JwtInvalidTokenError("Token is invalid or expired")

    # Verify decoded password reset token if it matches the token attributes in database
    formatted_token = JwtFormSchema.model_validate(decoded_token, from_attributes=True)
    db_user = self.user_repository.get_user_by_uuid(formatted_token.sub)

    if not db_user:
      logger.error(f"Token is not associated with any user - {payload.token}")
      raise JwtInvalidTokenError("Token is invalid or expired")

    token_sub_match = formatted_token.sub == db_user.uuid
    token_family_match = formatted_token.family_id == db_token.family_id

    if not token_sub_match or not token_family_match:
      logger.error(
        f"Token is not associated with any user, family_id does not match or expired - {payload.token}"
      )
      raise JwtInvalidTokenError("Token is invalid or expired")

    # Update user password
    self.user_repository.update_password(
      db_user.id, self.password_service.password_hash(payload.new_password)
    )

    # Revoke other password reset token that are related to the user
    self.repository.revoke_user_active_tokens(db_user.id, TokenType.PASSWORD_UPDATE)

    # Single transaction for all operations
    try:
      self.db.commit()
      return True
    except Exception as e:
      self.db.rollback()
      raise e
