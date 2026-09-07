from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
  email: EmailStr
  first_name: str = Field(..., nullable=False, description="First name")
  last_name: str = Field(..., nullable=False, description="Last name")
  address: str = Field(..., nullable=True, description="Address")
  phone_number: str = Field(..., nullable=True, description="Phone number")


class UserSchema(UserBaseSchema):
  id: int
  uuid: str
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None


class UserCreateSchema(UserBaseSchema):
  password: str = Field(..., min_length=8, max_length=20, description="Password")


class UserCreateResponseSchema(UserBaseSchema):
  uuid: str
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None


class UserUpdateSchema(UserBaseSchema):
  pass


class UserUpdateResponseSchema(UserBaseSchema):
  uuid: str
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None
