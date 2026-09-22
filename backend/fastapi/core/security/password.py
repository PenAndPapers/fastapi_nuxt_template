from passlib.context import CryptContext

from core.schema import NonEmptyStr

# Create a CryptContext instance with the desired hash algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password: NonEmptyStr) -> str:
  """
  Hash a password using bcrypt.

  Args:
      password: The password to hash.

  Returns:
      str: The hashed password.
  """
  return pwd_context.hash(password)


def verify_password(password: NonEmptyStr, hashed_password: NonEmptyStr) -> bool:
  """
  Verify a password against a hashed password.

  Args:
      password: The password to verify.
      hashed_password: The hashed password to compare against.

  Returns:
      bool: True if the password matches the hashed password, False otherwise.
  """
  return pwd_context.verify(password, str(hashed_password))
