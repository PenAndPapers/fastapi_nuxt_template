from core.database import DatabaseDep

from .model import Permission, Role, User


class UserRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = User

  def get_user_with_permissions(self, user_id: int) -> User | None:
    from sqlalchemy.orm import joinedload

    return (
      self.db.query(User)
      .options(joinedload(User.roles).joinedload(Role.permissions))
      .filter(User.id == user_id)
      .first()
    )

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
