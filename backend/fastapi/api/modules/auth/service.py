from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository

from .exception import InvalidCredentialsError
from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository
from .schema import AuthLoginSchema, AuthRegisterSchema, SessionToken, TokenType


class AuthService:
  def __init__(
    self,
    repository: AuthRepository,
    user_repository: UserRepository,
    user_role_repository: UserRoleRepository,
    jwt_service: JwtService,
    password_service: PasswordService,
  ) -> None:
    self.repository = repository
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
    # - rate limiting.
    # - send OTP if first time login within 24 hours via email.

    db_user = self.user_repository.get_user_by_email(user.email)
    is_password_invalid = db_user and not self.password_service.verify_password(
      user.password, db_user.password
    )

    if not db_user or is_password_invalid:
      raise InvalidCredentialsError("Incorrect email or password")

    family_id = self.jwt_service.get_token_jti()

    access_token, access_exp = self.jwt_service.create_token(
      TokenType.ACCESS, db_user.uuid, family_id
    )
    refresh_token, refresh_exp = self.jwt_service.create_token(
      TokenType.REFRESH, db_user.uuid, family_id
    )

    return SessionToken(
      access_token=access_token,
      access_exp=access_exp,
      refresh_token=refresh_token,
      refresh_exp=refresh_exp,
    )
