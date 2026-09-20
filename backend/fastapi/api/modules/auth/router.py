from fastapi import APIRouter, status

from api.modules.user.schema import UserCreateResponseSchema
from core.schema import GenericResponseMessage

from .dependency import AuthServiceDep
from .schema import (
  FormAuthForgetPasswordSchema,
  FormAuthLoginSchema,
  FormAuthRegisterSchema,
  FormAuthResetPasswordSchema,
  SessionTokenResponseSchema,
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(
  user: FormAuthRegisterSchema, auth_service: AuthServiceDep
) -> UserCreateResponseSchema:
  """
  Register a new user.

  This endpoint handle user registration, including validating input, creating a new user
  and assigning role to user.
  """
  new_user = auth_service.register(user)

  return new_user


@router.post("/login", status_code=status.HTTP_200_OK, summary="Login user")
def login(user: FormAuthLoginSchema, auth_service: AuthServiceDep) -> SessionTokenResponseSchema:
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
  user: FormAuthForgetPasswordSchema, auth_service: AuthServiceDep
) -> GenericResponseMessage:
  auth_service.forget_password(user)

  return GenericResponseMessage(
    message=f"Email has been sent to {user.email} with password reset instructions."
  )


@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Reset password for user")
def reset_password(
  payload: FormAuthResetPasswordSchema, auth_service: AuthServiceDep
) -> GenericResponseMessage:
  auth_service.reset_password(payload)

  return GenericResponseMessage(message="Password reset successfully.")


@router.post("/verify-email", summary="Verify user email")
def verify_email() -> dict[str, str]:
  # TODO: Add user email verification logic
  # This endpoint should handle user email verification, including validating input,
  # updating user's email status and returning success message.
  return {"message": "verify email endpoint"}
