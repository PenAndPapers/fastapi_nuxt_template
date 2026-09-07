import jwt
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class JwtPayload(BaseModel):
  sub: str
  name: str
  admin: bool


class SigningKeyResponse(BaseModel):
  token: str
  decoded: JwtPayload


PRIVATE_KEY = open("/app/certs/private_key.pem", "r").read()
PUBLIC_KEY = open("/app/certs/public_key.pem", "r").read()


@router.post("/register", summary="Register a new user")
def register() -> dict[str, str]:
  # TODO: Add user registration logic
  # This endpoint should handle user registration, including validating input, creating a new user
  # and sending verification emails.
  return {"message": "register endpoint"}


@router.post("/login", summary="Login user")
def login() -> dict[str, str]:
  # TODO: Add user login logic
  # This endpoint should handle user login, including validating input, authenticating user
  # and returning token.
  return {"message": "login endpoint"}


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


@router.post("/forget-password", summary="Forget password for user")
def forget_password() -> dict[str, str]:
  # TODO: Add user forget password logic
  # This endpoint should handle user forget password, including validating input,
  # sending OTP to user's email and updating user's password.
  return {"message": "forget password endpoint"}


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
def get_signing_key() -> SigningKeyResponse:
  payload = {"sub": "1234567890", "name": "John Doe", "admin": True}

  # Encode payload into a JWT string using private key
  token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256")

  # Decode and verify the JWT string using public key
  decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"])

  return SigningKeyResponse(token=token, decoded=JwtPayload(**decoded))
