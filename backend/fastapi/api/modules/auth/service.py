from api.modules.user.model import User
from api.modules.user.repository import UserRepository
from api.modules.user.schema import UserCreateSchema

from .jwt.service import JwtService
from .password.service import PasswordService
from .repository import AuthRepository


class AuthService:
  def __init__(
    self,
    repository: AuthRepository,
    user_repository: UserRepository,
    jwt_service: JwtService,
    password_service: PasswordService,
  ) -> None:
    self.repository = repository
    self.user_repository = user_repository
    self.jwt_service = jwt_service
    self.password_service = password_service

  def create_user(self, user: UserCreateSchema) -> User:
    # TODO: Add user creation logic
    # This endpoint should handle:
    # - user creation,
    # - password hashing,
    # - validating input,
    # - creating a new user
    # - sending verification emails.

    # Hash password
    role = user.role
    user.password = self.password_service.password_hash(user.password)

    # remove role from user so it matches user table schema
    del user.role

    # Create user repository with access to database
    return self.user_repository.create_user(user, role)
