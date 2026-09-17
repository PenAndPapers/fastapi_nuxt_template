from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


# ------------------------------------------------------------------------------------------------------------------------------------------------
# User Enums
# ------------------------------------------------------------------------------------------------------------------------------------------------
class EnumUserRole(StrEnum):
  ADMIN = "admin"
  EDITOR = "editor"
  PUBLISHER = "publisher"
  SUPER_ADMIN = "super_admin"
  USER = "user"


class EnumUserPermission(StrEnum):
  ALL = "all"
  USER_CREATE = "user:create"
  USER_DELETE = "user:delete"
  USER_READ = "user:read"
  USER_UPDATE = "user:update"
  CONTENT_CREATE = "content:create"
  CONTENT_DELETE = "content:delete"
  CONTENT_PUBLISH = "content:publish"
  CONTENT_READ = "content:read"
  CONTENT_UPDATE = "content:update"

  @property
  def description(self) -> str:
    _descriptions = {
      EnumUserPermission.ALL: "Full access to everything",
      EnumUserPermission.USER_CREATE: "Create user",
      EnumUserPermission.USER_DELETE: "Delete user data",
      EnumUserPermission.USER_READ: "Read user data",
      EnumUserPermission.USER_UPDATE: "Modify user data",
      EnumUserPermission.CONTENT_CREATE: "Create content",
      EnumUserPermission.CONTENT_DELETE: "Delete content",
      EnumUserPermission.CONTENT_PUBLISH: "Publish content",
      EnumUserPermission.CONTENT_READ: "Read content",
      EnumUserPermission.CONTENT_UPDATE: "Modify content",
    }
    return _descriptions[self]


# ------------------------------------------------------------------------------------------------------------------------------------------------
# User Request and Response Schemas
# ------------------------------------------------------------------------------------------------------------------------------------------------
class UserBaseSchema(BaseModel):
  email: EmailStr = Field(
    ...,
    description="Email address",
    json_schema_extra={"nullable": False, "example": "johndoe@example.com"},
  )
  first_name: str = Field(
    ...,
    description="First name",
    json_schema_extra={"nullable": False, "example": "John"},
  )
  last_name: str = Field(
    ...,
    description="Last name",
    json_schema_extra={"nullable": False, "example": "Doe"},
  )
  address: str = Field(
    ...,
    description="Address",
    json_schema_extra={"nullable": True, "example": "123 Main St, Anytown, USA"},
  )
  phone_number: str = Field(
    ...,
    description="Phone number",
    json_schema_extra={"nullable": True, "example": "+12345678901"},
  )


class UserCreateSchema(UserBaseSchema):
  password: str = Field(
    ...,
    min_length=8,
    max_length=20,
    description="Password",
    json_schema_extra={"example": "P@ssw0rd#123"},
  )
  role: EnumUserRole = Field(
    ..., description="User role", json_schema_extra={"example": EnumUserRole.USER.value}
  )


class UserCreateResponseSchema(UserBaseSchema):
  uuid: str
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None

  model_config = {"from_attributes": True}


class UserUpdateSchema(UserBaseSchema):
  pass


class UserUpdateResponseSchema(UserBaseSchema):
  uuid: str
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None
