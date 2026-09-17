from core.database import DatabaseDep
from core.schema import PositiveInt

from .exception import UserOrRoleNotFoundExceptionError
from .model import Permission, Role, User, UserRole
from .schema import EnumUserRole, UserCreateSchema


class UserRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = User

  def create_user(self, user: UserCreateSchema) -> User:
    new_user = User(**user.model_dump())
    self.db.add(new_user)
    self.db.commit()
    self.db.refresh(new_user)

    return new_user

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


class UserRoleRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = UserRole

  def assign_role(self, user_id: PositiveInt, role: EnumUserRole) -> UserRole:
    db_user = self.db.query(User).filter(User.id == user_id).first()
    db_role = self.db.query(Role).filter(Role.name == role.value).first()

    if not db_user or not db_role:
      raise UserOrRoleNotFoundExceptionError()

    user_role = UserRole(user_id=db_user.id, role_id=db_role.id)
    self.db.add(user_role)
    self.db.commit()
    self.db.refresh(user_role)

    return user_role


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
