from api.modules.user.model import User
from api.modules.user.repository import UserRepository, UserRoleRepository
from api.modules.user.schema import UserCreateSchema

from .exception import InvalidCredentialsError
from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository
from .schema import AuthLoginSchema


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

  def register(self, user: UserCreateSchema) -> User:
    # TODO:
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

  def login(self, user: AuthLoginSchema) -> User | None:
    db_user = self.user_repository.get_user_by_email(user.email)

    if not db_user or not self.password_service.verify_password(user.password, db_user.password):
      raise InvalidCredentialsError("Incorrect email or password")

    return db_user
