from pydantic import BaseModel, EmailStr, Field

from api.modules.user.schema import UserCreateSchema


class JwtPayload(BaseModel):
  sub: str
  name: str
  admin: bool


class SigningKeyResponse(BaseModel):
  token: str
  decoded: JwtPayload


class AuthRegisterSchema(UserCreateSchema):
  pass


class AuthLoginSchema(BaseModel):
  email: EmailStr
  password: str = Field(..., min_length=8, max_length=20, description="Password")


class AuthForgetPasswordSchema(BaseModel):
  email: EmailStr


class AuthResetPasswordSchema(BaseModel):
  email: EmailStr
  password: str = Field(..., min_length=8, max_length=20, description="New password")
  confirm_password: str = Field(
    ..., min_length=8, max_length=20, description="Confirm new password"
  )
