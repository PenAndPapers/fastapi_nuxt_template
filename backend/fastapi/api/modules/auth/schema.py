from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from api.modules.user.schema import UserCreateSchema


class TokenType(StrEnum):
  ACCESS = "access"
  REFRESH = "refresh"
  CONFIRM_EMAIL = "confirm_email"
  PASSWORD_UPDATE = "password_update"  # noqa: S105


class GeneratedToken(BaseModel):
  encoded: str
  exp: int
  family_id: str


class TokenSchema(BaseModel):
  token_hash: str = Field(..., description="Hashed token string.")
  token_type: TokenType = Field(..., description="Token type.")
  expires_at: datetime = Field(..., description="Expiration time as a datetime object.")
  is_revoked: bool = Field(False, description="Is the token revoked?")
  user_id: int = Field(..., description="User ID associated with the token.")
  device_id: int = Field(..., description="Device ID associated with the token.")
  family_id: str = Field(..., description="Family ID associated with the token.")

  model_config = {"from_attributes": True}


class SessionToken(BaseModel):
  access_token: str = Field(..., description="Access token for API requests.")
  access_exp: int = Field(
    ..., description="Expiration time as a Unix epoch timestamp (seconds) for the access token."
  )
  refresh_token: str = Field(..., description="Refresh token for obtaining new access tokens.")
  refresh_exp: int = Field(
    ..., description="Expiration time as a Unix epoch timestamp (seconds) for the refresh token."
  )

  model_config = {"from_attributes": True}


class DeviceSchema(BaseModel):
  client_device_id: str = Field(
    ..., description="Client device ID.", json_schema_extra={"example": "1234567890"}
  )
  device_type: str | None = Field(
    None,
    description="Device type (e.g., 'PC', 'Mobile', 'Tablet').",
    json_schema_extra={"example": "Mobile"},
  )
  os: str | None = Field(
    None,
    description="Operating system (e.g., 'Windows', 'macOS', 'Linux').",
    json_schema_extra={"example": "macOS"},
  )
  browser: str | None = Field(
    None,
    description="Browser (e.g., 'Chrome', 'Firefox', 'Safari').",
    json_schema_extra={"example": "Chrome"},
  )
  ip_address: str | None = Field(
    None, description="IP address (IPv4 or IPv6)", json_schema_extra={"example": "192.168.1.1"}
  )
  latitude: float | None = Field(
    None,
    description="Latitude of the user's location (if available)",
    json_schema_extra={"example": 37.7749},
  )
  longitude: float | None = Field(
    None,
    description="Longitude of the user's location (if available)",
    json_schema_extra={"example": 122.4194},
  )

  model_config = {"from_attributes": True}


class JwtPayload(BaseModel):
  """
  Standardized JWT Payload schema following RFC 7519 specifications.
  Enforces required claims for stateless authentication and token rotation workflows.
  """

  # --- Token Purpose & Classification ---
  token_type: TokenType = Field(
    ...,
    description="Distinguishes token purpose ('access' vs 'refresh'). "
    "Handlers MUST validate this claim to prevent refresh tokens from being used on general API endpoints.",
  )

  # --- Registered Claims (RFC 7519 Timestamps) ---
  exp: int = Field(
    ...,
    description="Expiration time as a Unix epoch timestamp (seconds). "
    "Requests after this timestamp MUST be rejected. (e.g., 15 mins for access, 7 days for refresh).",
  )
  nbf: int = Field(
    ...,
    description="Not Before time as a Unix epoch timestamp (seconds). "
    "The token MUST NOT be accepted before this time (typically set to match 'iat').",
  )
  iat: int = Field(
    ...,
    description="Issued At time as a Unix epoch timestamp (seconds). "
    "Indicates when the token was generated.",
  )

  # --- Issuer & Audience Scope ---
  iss: str = Field(
    ...,
    description="Issuer identifier (e.g., 'https://api.myapp.com'). "
    "Identifies the backend auth service that minted this token.",
  )
  aud: str = Field(
    ...,
    description="Audience identifier (e.g., 'https://app.myapp.com'). "
    "Identifies the recipient or target application service this token is intended for.",
  )

  # --- Subject & Tracking Identifiers ---
  sub: str = Field(
    ...,
    description="Subject identifier. The unique ID (UUID string) of the user who owns this session.",
  )
  jti: str = Field(
    ...,
    description="JWT ID (UUID v4). A globally unique identifier for THIS SPECIFIC token instance. "
    "Used to store blacklisted/revoked tokens in Redis.",
  )
  family_id: str = Field(
    ...,
    description="Token Family ID (UUID v4). Shared ID linking an access token and its refresh token chain. "
    "Used to invalidate the ENTIRE session family in Redis if refresh token theft/reuse is detected.",
  )

  model_config = {"from_attributes": True, "extra": "forbid", "use_enum_values": True}


class SigningKeyResponse(BaseModel):
  token: str
  decoded: JwtPayload


class AuthRegisterSchema(UserCreateSchema):
  pass


class AuthLoginSchema(BaseModel):
  email: EmailStr = Field(
    ...,
    description="Email address",
    json_schema_extra={"nullable": False, "example": "johndoe@example.com"},
  )
  password: str = Field(
    ...,
    min_length=8,
    max_length=20,
    description="Password",
    json_schema_extra={"example": "P@ssw0rd#123"},
  )


class AuthForgetPasswordSchema(BaseModel):
  email: EmailStr = Field(
    ..., description="Email address", json_schema_extra={"example": "johndoe@example.com"}
  )
  device: DeviceSchema


class AuthResetPasswordSchema(BaseModel):
  token: str = Field(
    ...,
    min_length=1,
    description="Reset password token",
    json_schema_extra={"example": "eyJhbGciOiJIU..."},
  )
  new_password: str = Field(
    ...,
    min_length=8,
    max_length=20,
    description="New password",
    json_schema_extra={"example": "P@ssw0rd#123"},
  )
  confirm_password: str = Field(
    ...,
    min_length=8,
    max_length=20,
    description="Confirm new password",
    json_schema_extra={"example": "P@ssw0rd#123"},
  )

  @model_validator(mode="after")
  def verify_password_match(self) -> Self:
    if self.new_password != self.confirm_password:
      raise ValueError("Passwords do not match")

    return self
