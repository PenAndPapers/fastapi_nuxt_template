import hashlib
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import AppBaseModel

if TYPE_CHECKING:
    from api.modules.user.model import User


class Auth(AppBaseModel):
    """
    Refresh Tokens / Session management.
    """

    __tablename__ = "auth_tokens"

    # Store hashed tokens (e.g., SHA-256 of the actual refresh token)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token_type: Mapped[str] = mapped_column(String(20), default="refresh")
    expires_at: Mapped[datetime] = mapped_column(index=True)
    is_revoked: Mapped[bool] = mapped_column(default=False, index=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    device_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="tokens")
    device: Mapped[Optional["Device"]] = relationship("Device", back_populates="tokens")

    __table_args__ = (
        # Composite index for rapid session validation
        Index("ix_auth_tokens_user_revoked", "user_id", "is_revoked"),
    )


class OneTimePin(AppBaseModel):
    """
    Logs and manages OTPs for authentication/MFA.
    """

    __tablename__ = "one_time_pins"

    # Store hashed PINs to prevent DB breach exposure
    pin_hash: Mapped[str] = mapped_column(String(64), index=True)
    purpose: Mapped[str] = mapped_column(String(30), default="login")  # login, reset_password
    expires_at: Mapped[datetime] = mapped_column(index=True)
    is_revoked: Mapped[bool] = mapped_column(default=False)
    is_used: Mapped[bool] = mapped_column(default=False)
    attempts: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="one_time_pins")


class Device(AppBaseModel):
    """
    Logs unique user devices and session origins.
    """

    __tablename__ = "devices"

    # Standardized fingerprinted ID or UUID from client
    client_device_id: Mapped[str] = mapped_column(String(255), index=True)
    device_type: Mapped[str | None] = mapped_column(String(50))
    os: Mapped[str | None] = mapped_column(String(50))
    browser: Mapped[str | None] = mapped_column(String(50))
    ip_address: Mapped[str | None] = mapped_column(String(45))  # Accommodates IPv6
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="devices")
    tokens: Mapped[list["Auth"]] = relationship("Auth", back_populates="devices")
