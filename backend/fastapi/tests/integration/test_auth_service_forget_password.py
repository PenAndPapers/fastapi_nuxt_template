from faker import Faker
from sqlalchemy.orm import Session

from api.modules.auth.password.service import PasswordService
from api.modules.auth.repository import AuthRepository
from api.modules.auth.schema import FormAuthForgetPasswordSchema, FormDeviceSchema, TokenType
from api.modules.auth.service import AuthService
from api.modules.user.model import User


def _sample_data(
  db_session: Session, faker: Faker
) -> dict[str, str | float | int | FormDeviceSchema]:
  session_id = hex(id(db_session))

  return {
    "email": f"test_integration_forgot_password_{session_id}_{faker.email()}",
    "password": faker.password(),
    "uuid": faker.uuid4(),
    "first_name": faker.first_name(),
    "last_name": faker.last_name(),
    "address": faker.address(),
    "phone_number": faker.phone_number(),
    "device": FormDeviceSchema(
      client_device_id=faker.uuid4(),
      device_type=faker.word(),
      os=faker.word(),
      browser=faker.word(),
      ip_address=faker.ipv4(),
      latitude=faker.latitude(),
      longitude=faker.longitude(),
    ),
  }


def test_forget_password_success_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = _sample_data(db_session, faker)
  # Arrange: Create user in DB
  hashed_pw = PasswordService().password_hash(data["password"])
  test_user = User(
    email=data["email"],
    password=hashed_pw,
    first_name=data["first_name"],
    last_name=data["last_name"],
    address=data["address"],
    phone_number=data["phone_number"],
    uuid=data["uuid"],
  )
  db_session.add(test_user)
  db_session.commit()

  forget_data = FormAuthForgetPasswordSchema(email=data["email"], device=data["device"])

  # Act
  result = auth_service.forget_password(forget_data)

  # Assert
  assert result is True  # Return True if token was created successfully

  # Check if token was stored in DB using the repository
  repo = AuthRepository(db_session)
  token = repo.get_user_latest_active_token_by_type(test_user.id, TokenType.PASSWORD_UPDATE)

  assert token is not None
  assert token.token_type == TokenType.PASSWORD_UPDATE.value


def test_forget_password_user_not_found_integration(
  auth_service: AuthService, db_session: Session, faker: Faker
) -> None:
  data = _sample_data(db_session, faker)
  # Use a different email that isn't in the DB
  forget_data = FormAuthForgetPasswordSchema(
    email=f"nonexistent_{faker.email()}", device=data["device"]
  )

  # Act
  result = auth_service.forget_password(forget_data)

  # Assert
  assert result is None  # Return None if user not found
