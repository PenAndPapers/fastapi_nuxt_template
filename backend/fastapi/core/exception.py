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
