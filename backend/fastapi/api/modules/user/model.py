from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import AppBaseModel


class User(AppBaseModel):
    __tablename__ = "users"

    uuid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Many-to-Many relationship to Role via UserRole
    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles", back_populates="users", lazy="selectin"
    )


class UserRole(AppBaseModel):
    """Junction table connecting Users and Roles."""

    __tablename__ = "user_roles"

    # Match foreign key types to AppBaseModel primary key (e.g., int or str/UUID)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)


class Role(AppBaseModel):
    """Role definition table."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(secondary="user_roles", back_populates="roles")
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permissions", back_populates="roles", lazy="selectin"
    )


class RolePermission(AppBaseModel):
    """Junction table connecting Roles and Permissions."""

    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), index=True
    )


class Permission(AppBaseModel):
    """Permission definition table."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship back to Role
    roles: Mapped[List["Role"]] = relationship(
        secondary="role_permissions", back_populates="permissions"
    )
