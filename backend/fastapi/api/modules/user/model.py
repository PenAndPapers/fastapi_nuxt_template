from typing import ClassVar

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.model import AppBaseModel


class User(AppBaseModel):
  """User definition table."""

  __tablename__ = "users"
  __table_args__: ClassVar[dict[str, str]] = {
    "comment": "User definition table. Each user can have multiple roles."
  }

  uuid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
  last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
  address: Mapped[str | None] = mapped_column(String(255), nullable=True)
  phone_number: Mapped[str | None] = mapped_column(String(255), nullable=True)

  # Many-to-Many relationship to Role via UserRole
  roles: Mapped[list["Role"]] = relationship(
    secondary="user_roles", back_populates="users", lazy="selectin"
  )


class UserRole(AppBaseModel):
  """Junction table connecting Users and Roles."""

  __tablename__ = "user_roles"
  __table_args__: ClassVar[dict[str, str]] = {
    "comment": "Junction table connecting Users and Roles."
  }

  # Match foreign key types to AppBaseModel primary key (e.g., int or str/UUID)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
  role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)


class Role(AppBaseModel):
  """Role definition table."""

  __tablename__ = "roles"
  __table_args__: ClassVar[dict[str, str]] = {
    "comment": "Role definition table. Each role can have multiple users and permissions."
  }

  name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
  description: Mapped[str | None] = mapped_column(String(255), nullable=True)

  # Relationships
  users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles")
  permissions: Mapped[list["Permission"]] = relationship(
    secondary="role_permissions", back_populates="roles", lazy="selectin"
  )


class RolePermission(AppBaseModel):
  """Junction table connecting Roles and Permissions."""

  __tablename__ = "role_permissions"
  __table_args__: ClassVar[dict[str, str]] = {
    "comment": "Junction table connecting Roles and Permissions."
  }

  role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
  permission_id: Mapped[int] = mapped_column(
    ForeignKey("permissions.id", ondelete="CASCADE"), index=True
  )


class Permission(AppBaseModel):
  """Permission definition table."""

  __tablename__ = "permissions"
  __table_args__: ClassVar[dict[str, str]] = {
    "comment": "Permission definition table. Each permission is associated with a role."
  }

  name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
  description: Mapped[str | None] = mapped_column(String(255), nullable=True)

  # Relationship back to Role
  roles: Mapped[list["Role"]] = relationship(
    secondary="role_permissions", back_populates="permissions"
  )
