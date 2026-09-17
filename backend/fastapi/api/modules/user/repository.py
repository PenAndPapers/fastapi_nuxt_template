from core.database import DatabaseDep

from .model import Permission, Role, User
from .schema import EnumUserRole, UserCreateSchema


class UserRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = User

  def create_user(self, user: UserCreateSchema, role: EnumUserRole) -> User:
    # 1. Create the Model instance from the schema
    user_entity = User(**user.model_dump())

    # 2. Add and commit to get the ID from the database
    self.db.add(user_entity)
    self.db.commit()

    # 3. Now user_entity.id is populated. Use it to set the role.
    self.set_user_role(user_entity.id, role)

    # 4. Refresh to get the latest state (including any DB-side defaults)
    self.db.refresh(user_entity)

    return user_entity

  def set_user_role(self, user_id: int, role: EnumUserRole) -> None:
    user = self.db.query(User).filter(User.id == user_id).first()
    if user:
      user.role = role
      self.db.commit()

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
