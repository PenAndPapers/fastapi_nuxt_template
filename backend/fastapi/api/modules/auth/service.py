from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository

from .exception import InvalidCredentialsError
from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository, DeviceRepository
from .schema import (
  AuthForgetPasswordSchema,
  AuthLoginSchema,
  AuthRegisterSchema,
  AuthResetPasswordSchema,
  DeviceSchema,
  SessionToken,
  TokenSchema,
  TokenType,
)


class AuthService:
  def __init__(
    self,
    repository: AuthRepository,
    device_repository: DeviceRepository,
    user_repository: UserRepository,
    user_role_repository: UserRoleRepository,
    jwt_service: JwtService,
    password_service: PasswordService,
  ) -> None:
    self.repository = repository
    self.device_repository = device_repository
    self.user_repository = user_repository
    self.user_role_repository = user_role_repository
    self.jwt_service = jwt_service
    self.password_service = password_service

  def register(self, user: AuthRegisterSchema) -> User:
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

  def login(self, user: AuthLoginSchema) -> SessionToken:
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

    return SessionToken(
      access_token=str(access_token.encoded),
      access_exp=access_token.exp,
      refresh_token=str(refresh_token.encoded),
      refresh_exp=refresh_token.exp,
    )

  def forget_password(self, user: AuthForgetPasswordSchema) -> bool:
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

    device_to_store = DeviceSchema(
      client_device_id=device.client_device_id,
      device_type=device.device_type,
      os=device.os,
      browser=device.browser,
      ip_address=device.ip_address,
      latitude=device.latitude,
      longitude=device.longitude,
    )

    token_to_store = TokenSchema(
      token_hash=str(forget_password_token.encoded),
      token_type=TokenType.PASSWORD_UPDATE,
      expires_at=forget_password_token.exp,
      family_id=forget_password_token.family_id,
      is_revoked=False,
    )

    # Store device token in database
    device = self.device_repository.store_device(
      device_to_store,
      user_id=db_user.id,
    )

    # Store token in database
    self.repository.store_token(token_to_store)

    return True

  def reset_password(self, payload: AuthResetPasswordSchema) -> bool:
    # TODO:
    # - rate limiting.
    # - verify password reset token.
    # - update user password.
    # - revoke password reset token.
    # - send success message to user's email.

    return True
