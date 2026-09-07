from .repository import AuthRepository


class AuthService:
  def __init__(self, repository: AuthRepository) -> None:
    self.repository = repository

  def create_user(self) -> None:
    pass
