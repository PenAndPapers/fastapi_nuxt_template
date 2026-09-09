import pytest

from api.modules.auth.password.service import PasswordService


@pytest.fixture
def password_service() -> PasswordService:
  return PasswordService()


def test_password_hash_returns_string(password_service: PasswordService) -> None:
  raw_password = "my_secure_password123"  # noqa: S105
  hashed = password_service.password_hash(raw_password)

  assert isinstance(hashed, str)
  assert hashed != raw_password
  assert len(hashed) > 0


def test_verify_password_success(password_service: PasswordService) -> None:
  raw_password = "my_secure_password123"  # noqa: S105
  hashed = password_service.password_hash(raw_password)

  is_valid = password_service.verify_password(raw_password, hashed)

  assert is_valid is True


def test_verify_password_failure(password_service: PasswordService) -> None:
  raw_password = "my_secure_password123"  # noqa: S105
  wrong_password = "wrong_password123"  # noqa: S105
  hashed = password_service.password_hash(raw_password)

  is_valid = password_service.verify_password(wrong_password, hashed)

  assert is_valid is False
