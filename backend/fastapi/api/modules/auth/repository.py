from datetime import UTC, datetime

from sqlalchemy import select

from core.database import DatabaseDep
from core.exception import DBExceptionError
from core.schema import NonEmptyStr, PositiveInt

from .model import AuthToken, Device
from .schema import FormDeviceSchema, TokenFormSchema, TokenType


class AuthRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = AuthToken

  def store_token(self, token: TokenFormSchema) -> AuthToken:
    new_token = AuthToken(**token.model_dump())
    self.db.add(new_token)

    return new_token

  def get_token_by_hash(self, token_hash: NonEmptyStr) -> AuthToken | None:
    query = select(self.model).where(self.model.token_hash == token_hash)
    return self.db.execute(query).scalar_one_or_none()

  def get_token_by_id(self, token_id: PositiveInt) -> AuthToken | None:
    query = select(self.model).where(self.model.id == token_id)
    return self.db.execute(query).scalar_one_or_none()

  def get_user_active_tokens_by_type(
    self, user_id: PositiveInt, token_type: TokenType
  ) -> list[AuthToken]:
    query = select(self.model).where(
      (self.model.token_type == token_type)
      & (self.model.user_id == user_id)
      & (self.model.is_revoked == False)  # noqa E712
    )
    tokens = list(self.db.execute(query).scalars().all())

    return tokens

  def revoke_token(self, token_id: PositiveInt) -> None:
    token = self.get_token_by_id(token_id)

    if not token:
      raise DBExceptionError("Operation not permitted")

    token.is_revoked = True

  def revoke_user_active_tokens(self, user_id: PositiveInt, token_type: TokenType) -> None:
    tokens = self.get_user_active_tokens_by_type(user_id, token_type)

    # revoke tokens and set deleted_at to current time
    for token in tokens:
      token.is_revoked = True
      token.deleted_at = datetime.now(UTC)


class DeviceRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Device

  def store_device(self, device: FormDeviceSchema, user_id: PositiveInt) -> Device:
    new_device = Device(**device.model_dump(), user_id=user_id)
    self.db.add(new_device)

    return new_device
