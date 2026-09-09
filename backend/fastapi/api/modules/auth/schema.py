from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.modules.user.schema import UserCreateSchema


class TokenType(StrEnum):
  ACCESS = "access"
  REFRESH = "refresh"
  CONFIRM_EMAIL = "confirm_email"
  PASSWORD_UPDATE = "password_update"  # noqa: S105

from api.modules.user.schema import UserCreateSchema


class JwtPayload(BaseModel):
  token_type: TokenType
  exp: int  # expiration time (timestamp)
  nbf: int  # valid before time (timestamp)
  iat: int  # issued at time (timestamp)
  iss: str  # issuer the backend e.g http://localhost:8000, http://app.dev
  aud: str  # intended audience frontend or other service e.g http://localhost:8000, http://api-service.com
  sub: str  # user's uuid who owns the token
  jti: str  # unique token identifier for revocation (uuid)

  model_config = ConfigDict(use_enum_values=True)


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
