from core.database import DatabaseDep

from .model import Permission, Role, User


class UserRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = User

  def get_user(self) -> None:
    pass


class RoleRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Role

  def get_role(self) -> None:
    pass


class PermissionRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Permission

  def get_permission(self) -> None:
    pass
