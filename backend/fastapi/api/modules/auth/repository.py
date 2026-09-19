from sqlalchemy import select

from core.database import DatabaseDep
from core.exception import DBExceptionError
from core.schema import NonEmptyStr, PositiveInt

from .model import Auth, Device
from .schema import DeviceSchema, TokenSchema


class AuthRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Auth

  def store_token(self, token: TokenSchema) -> Auth:
    new_token = Auth(**token.model_dump())
    self.db.add(new_token)

    return new_token

  def get_token_by_hash(self, token_hash: NonEmptyStr) -> Auth | None:
    query = select(self.model).where(self.model.token_hash == token_hash)
    return self.db.execute(query).scalar_one_or_none()

  def get_token_by_id(self, token_id: PositiveInt) -> Auth | None:
    query = select(self.model).where(self.model.id == token_id)
    return self.db.execute(query).scalar_one_or_none()

  def revoke_token(self, token_id: PositiveInt) -> None:
    token = self.get_token_by_id(token_id)

    if not token:
      raise DBExceptionError("Operation not permitted")

    token.is_revoked = True


class DeviceRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Device

  def store_device(self, device: DeviceSchema, user_id: PositiveInt) -> Device:
    new_device = Device(**device.model_dump(), user_id=user_id)
    self.db.add(new_device)

    return new_device
