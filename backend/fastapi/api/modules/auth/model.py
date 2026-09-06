from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import AppBaseModel

if TYPE_CHECKING:
    from api.modules.user.model import User


class Auth(AppBaseModel):
    """
    Auth model.
    """

    __tablename__ = "auth"

    token: Mapped[str] = mapped_column(index=True)
    token_type: Mapped[str] = mapped_column(index=True)
    expires_at: Mapped[datetime] = mapped_column(index=True)
    is_revoked: Mapped[bool] = mapped_column(index=True, default=False)
    user_id: Mapped[int] = mapped_column(index=True)
    device_id: Mapped[str] = mapped_column(index=True)

    user: Mapped["User"] = relationship("User", back_populates="tokens")
    device: Mapped["Device"] = relationship("Device", back_populates="tokens")


class OneTimePin(AppBaseModel):
    """
    OneTimePin model. Logs one-time pin information.
    """

    __tablename__ = "one_time_pins"
    pin: Mapped[str] = mapped_column(index=True)
    expires_at: Mapped[datetime] = mapped_column(index=True)
    is_revoked: Mapped[bool] = mapped_column(index=True, default=False)
    is_used: Mapped[bool] = mapped_column(index=True, default=False)
    user_id: Mapped[int] = mapped_column(index=True)

    user: Mapped["User"] = relationship("User", back_populates="one_time_pins")


class Device(AppBaseModel):
    """
    Device model. Logs device information.
    """

    __tablename__ = "devices"
    device_id: Mapped[str] = mapped_column(index=True)
    device_type: Mapped[str] = mapped_column(index=True)
    os: Mapped[str] = mapped_column(index=True)
    browser: Mapped[str] = mapped_column(index=True)
    ip: Mapped[str] = mapped_column(index=True)
    latitude: Mapped[float] = mapped_column(index=True)
    longitude: Mapped[float] = mapped_column(index=True)
