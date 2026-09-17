from core.exception import AppExceptionError


class UserError(AppExceptionError):
  pass


class UserNotFoundExceptionError(UserError):
  status_code = 404
  error_code = "USER_NOT_FOUND"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "Error: User not found"
    super().__init__(self.message)


class UserOrRoleNotFoundExceptionError(UserError):
  status_code = 404
  error_code = "USER_OR_ROLE_NOT_FOUND"

  def __init__(self, message: str | None = None) -> None:
    self.message = message or "Error: User or role not found"
    super().__init__(self.message)
