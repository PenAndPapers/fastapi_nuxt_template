from passlib.context import CryptContext

from core.schema import NonEmptyStr

# Create a CryptContext instance with the desired hash algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
  """
  Password service to hash and verify passwords. Use bcrypt algorithm.
  """

  def password_hash(self, password: NonEmptyStr) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)

  def verify_password(self, password: NonEmptyStr, hashed_password: NonEmptyStr) -> bool:
    """
    Verify a password against a hashed password.
    """
    return pwd_context.verify(password, str(hashed_password))
