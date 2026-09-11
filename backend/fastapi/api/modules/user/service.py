from .repository import UserRepository


class UserService:
  def __init__(self, repository: UserRepository) -> None:
    self.repository = repository

  def get_user(self) -> None:
    pass
