from .repository import UserRepository


class UserService:
  def __init__(self, repository: UserRepository) -> None:
    self.repository = repository

  def get_user_permissions(self, user_id: int) -> set[str]:
    user = self.repository.get_user_with_permissions(user_id)
    if not user:
      return set()

    permissions = set()
    for role in user.roles:
      for perm in role.permissions:
        permissions.add(perm.name)
    return permissions

  def get_user(self) -> None:
    pass
