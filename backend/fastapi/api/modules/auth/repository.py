from core.database import DatabaseDep

from .model import Auth, Device
from .schema import DeviceSchema, TokenSchema


class AuthRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Auth

  def store_token(self, token: TokenSchema) -> Auth:
    new_token = Auth(**token.model_dump())
    self.db.add(new_token)

    try:
      self.db.commit()
      self.db.refresh(new_token)
      return new_token
    except Exception as e:
      self.db.rollback()
      raise e


class DeviceRepository:
  def __init__(self, db: DatabaseDep) -> None:
    self.db = db
    self.model = Device

  def store_device(self, device: DeviceSchema, user_id: int) -> Device:
    new_device = Device(**device.model_dump(), user_id=user_id)
    self.db.add(new_device)

    try:
      self.db.commit()
      self.db.refresh(new_device)
      return new_device
    except Exception as e:
      self.db.rollback()
      raise e
