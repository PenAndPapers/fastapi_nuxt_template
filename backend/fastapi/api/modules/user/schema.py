from datetime import datetime

from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    address: str | None = None
    phone_number: str | None = None


class UserSchema(UserBaseSchema):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class UserCreateSchema(UserBaseSchema):
    password: str


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


class UserLoginSchema(BaseModel):
    email: str
    password: str
