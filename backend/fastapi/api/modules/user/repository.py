from pydantic import EmailStr
from sqlalchemy import select

from core.database import DatabaseDep
from core.exception import DBExceptionError
from core.schema import PositiveInt

from .exception import UserAlreadyExistExceptionError, UserOrRoleNotFoundExceptionError
from .model import Permission, Role, User, UserRole
from .schema import EnumUserRole, UserCreateSchema


class UserRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = User

  def create_user(self, user: UserCreateSchema) -> User:
    new_user = User(**user.model_dump())
    self.db.add(new_user)

    try:
      self.db.commit()
      self.db.refresh(new_user)
      return new_user
    except Exception as e:
      self.db.rollback()
      raise UserAlreadyExistExceptionError() from e

  def get_user_by_email(self, email: EmailStr) -> User | None:
    query = select(User).filter(User.email == email)
    result = self.db.execute(query).scalar_one_or_none()

    return result

  def get_user_by_id(self, user_id: PositiveInt) -> User | None:
    query = select(User).filter(User.id == user_id)
    result = self.db.execute(query).scalar_one_or_none()
    return result

  def get_user_by_uuid(self, uuid: str) -> User | None:
    query = select(User).filter(User.uuid == uuid)
    result = self.db.execute(query).scalar_one_or_none()
    return result

  def get_user_with_permissions(self, user_id: int) -> User | None:
    from sqlalchemy.orm import joinedload

    return (
      self.db.query(User)
      .options(joinedload(User.roles).joinedload(Role.permissions))
      .filter(User.id == user_id)
      .first()
    )

  def update_password(self, user_id: PositiveInt, new_password: str) -> User | None:
    db_user = self.get_user_by_id(user_id)

    if not db_user:
      raise DBExceptionError("Unable to process request")

    db_user.password = new_password

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
