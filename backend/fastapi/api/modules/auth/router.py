from fastapi import APIRouter, status

from api.modules.user.schema import UserCreateResponseSchema
from core.schema import GenericResponseMessage

from .dependency import AuthServiceDep
from .schema import (
  AuthForgetPasswordSchema,
  AuthLoginSchema,
  AuthRegisterSchema,
  JwtPayload,
  SessionToken,
  SigningKeyResponse,
  TokenType,
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(user: AuthRegisterSchema, auth_service: AuthServiceDep) -> UserCreateResponseSchema:
  """
  Register a new user.

  This endpoint handle user registration, including validating input, creating a new user
  and assigning role to user.
  """
  new_user = auth_service.register(user)

  return new_user


@router.post("/login", status_code=status.HTTP_200_OK, summary="Login user")
def login(user: AuthLoginSchema, auth_service: AuthServiceDep) -> SessionToken:
  # TODO: Add user login logic
  # This endpoint should handle user login, including validating input, authenticating user
  # and returning token.

  session_token = auth_service.login(user)

  return session_token


@router.post("/refresh-token", summary="Refresh user token")
def refresh_token() -> dict[str, str]:
  # TODO: Add user token refresh logic
  # This endpoint should handle user token refresh, including validating input, refreshing token
  # and returning new token.
  return {"message": "refresh token endpoint"}


@router.post("/otp", summary="Generate user OTP")
def otp() -> dict[str, str]:
  # TODO: Add user OTP generation logic
  # This endpoint should handle user OTP generation, including validating input, generating OTP
  # and sending OTP to user's email.
  return {"message": "otp endpoint"}


@router.post("/logout", summary="Logout user")
def logout() -> dict[str, str]:
  # TODO: Add user logout logic
  # This endpoint should handle user logout, including invalidating token and logging out user.
  return {"message": "logout endpoint"}


@router.post("/forget-password", status_code=status.HTTP_200_OK, summary="Forget password for user")
def forget_password(
  user: AuthForgetPasswordSchema, auth_service: AuthServiceDep
) -> GenericResponseMessage:
  auth_service.forget_password(user)

  return GenericResponseMessage(
    message=f"Email has been sent to {user.email} with password reset instructions."
  )


@router.post("/reset-password", summary="Reset password for user")
def reset_password() -> dict[str, str]:
  # TODO: Add user reset password logic
  # This endpoint should handle user reset password, including validating input,
  # updating user's password and returning success message.
  return {"message": "reset password endpoint"}


@router.post("/verify-email", summary="Verify user email")
def verify_email() -> dict[str, str]:
  # TODO: Add user email verification logic
  # This endpoint should handle user email verification, including validating input,
  # updating user's email status and returning success message.
  return {"message": "verify email endpoint"}


@router.get("/signing-key", summary="Get signing key")
def get_signing_key(auth_service: AuthServiceDep) -> SigningKeyResponse:
  payload = JwtPayload(
    token_type=TokenType.ACCESS,
    exp=1791524531,
    nbf=1788932531,
    iat=1788932531,
    iss="http://localhost:8000",
    aud="http://localhost:3000",
    sub="a8s9675d98g76as78dgas8",
    jti="a897s6d6h7986asdfa7s8d",
    family_id="a8967sbhdf67asd6f978a6s5dg",
  )

  # Encode payload into a JWT string using private key
  token = auth_service.jwt_service.encode(payload)

  # Decode and verify the JWT string using public key
  decoded = auth_service.jwt_service.decode(token, audience=payload.aud, issuer=payload.iss)

  return SigningKeyResponse(token=token, decoded=JwtPayload(**decoded))


@router.get("/jwt", summary="Get JWT token")
def get_jwt_token(auth_service: AuthServiceDep) -> SessionToken:
  payload = {"sub": "user_uuid_a8s9675d98g76as78dgas8"}  # user uuid
  family_id = auth_service.jwt_service.get_token_jti()  # family identifier

  # Generate access token
  access_token_claims = auth_service.jwt_service.get_default_jwt_claims(TokenType.ACCESS)
  access_token_claims["token_type"] = TokenType.ACCESS.value
  access_token_claims["sub"] = payload["sub"]
  access_token_claims["jti"] = auth_service.jwt_service.get_token_jti()
  access_token_claims["family_id"] = family_id

  # Generate refresh token
  refresh_token_claims = auth_service.jwt_service.get_default_jwt_claims(TokenType.REFRESH)
  refresh_token_claims["token_type"] = TokenType.REFRESH.value
  refresh_token_claims["sub"] = payload["sub"]
  refresh_token_claims["jti"] = auth_service.jwt_service.get_token_jti()
  refresh_token_claims["family_id"] = family_id

  access_token = auth_service.jwt_service.encode(JwtPayload(**access_token_claims))
  refresh_token = auth_service.jwt_service.encode(JwtPayload(**refresh_token_claims))

  return {
    "access_token": access_token,
    "exp": access_token_claims["exp"],
    "refresh_token": refresh_token,
    "refresh_exp": refresh_token_claims["exp"],
  }


@router.post("/hash-password", summary="Hash password")
def hash_password(auth_service: AuthServiceDep) -> dict[str, str | bool]:
  hashed_password = auth_service.password_service.password_hash("3x@mPle@t35t")
  verify_password = auth_service.password_service.verify_password("3x@mPle@t35t", hashed_password)
  return {"hashed_password": hashed_password, "is_match": verify_password}
