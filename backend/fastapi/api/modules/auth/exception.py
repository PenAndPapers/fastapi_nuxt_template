class AuthError(Exception):
    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass
