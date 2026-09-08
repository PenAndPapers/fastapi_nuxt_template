from core.exception import AppExceptionError


class AuthError(AppExceptionError):
  status_code = 401
  error_code = "UNAUTHORIZED"

  def __init__(self, message: str | None) -> None:
    self.message = message or "Error: Unauthorized"
    super().__init__(self.message)


class InvalidCredentialsError(AppExceptionError):
  status_code = 400
  error_code = "INVALID_CREDENTIALS"

  def __init__(self, message: str | None) -> None:
    self.message = message or "Error: Invalid credentials"
    super().__init__(self.message)


class UnauthorizedAccessError(AppExceptionError):
  status_code = 403
  error_code = "UNAUTHORIZED_ACCESS"

  def __init__(self, message: str | None) -> None:
    self.message = message or "Error: Unauthorized access"
    super().__init__(self.message)


class JwtExpiredError(AppExceptionError):
  status_code = 401
  error_code = "JWT_EXPIRED"

  def __init__(self, message: str | None) -> None:
    self.message = message or "Error: JWT expired"
    super().__init__(self.message)


class JwtInvalidTokenError(AppExceptionError):
  status_code = 401
  error_code = "JWT_INVALID_TOKEN"

  def __init__(self, message: str | None) -> None:
    self.message = message or "Error: JWT invalid token"
    super().__init__(self.message)
