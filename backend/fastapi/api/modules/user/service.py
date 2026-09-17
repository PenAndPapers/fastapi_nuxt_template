from .exception import UserNotFoundExceptionError
from .repository import UserRepository
from .schema import UserCreateSchema


class UserService:
  def __init__(self, repository: UserRepository) -> None:
    self.repository = repository

  def create_user(self, user: UserCreateSchema) -> None:
    self.repository.create_user(user)

  def get_user_permissions(self, user_id: int) -> set[str]:
    user = self.repository.get_user_with_permissions(user_id)
    if not user:
      raise UserNotFoundExceptionError()

    return {perm.name for role in user.roles for perm in role.permissions}

  def get_user(self) -> None:
    pass
