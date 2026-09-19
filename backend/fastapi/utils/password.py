import re


def is_valid_password(password: str) -> str:
  pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_@$#%&*]).+$"

  if not re.match(pattern, password):
    raise ValueError(
      "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (_@$#%&*)."
    )

  return password
