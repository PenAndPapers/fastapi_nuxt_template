class AppExceptionError(Exception):
  status_code = 500
  error_code = "INTERNAL_SERVER_ERROR"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "An unexpected error occured"
    super().__init__(self.message)


class DBExceptionError(AppExceptionError):
  status_code = 500
  error_code = "DB_ERROR"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "Database error occured"
    super().__init__(self.message)


class JwtExpiredError(AppExceptionError):
  status_code = 401
  error_code = "JWT_EXPIRED"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "Token is expired"
    super().__init__(self.message)


class JwtInvalidTokenError(AppExceptionError):
  status_code = 401
  error_code = "JWT_INVALID_TOKEN"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "Token is invalid"
    super().__init__(self.message)
