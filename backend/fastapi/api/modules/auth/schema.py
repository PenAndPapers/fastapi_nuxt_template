from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.modules.user.schema import UserCreateSchema


class TokenType(StrEnum):
  ACCESS = "access"
  REFRESH = "refresh"
  CONFIRM_EMAIL = "confirm_email"
  PASSWORD_UPDATE = "password_update"  # noqa: S105


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

  model_config = ConfigDict(
    use_enum_values=True,
    # Strips extra fields or validates strict payload shapes if needed
    extra="forbid",
  )


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
