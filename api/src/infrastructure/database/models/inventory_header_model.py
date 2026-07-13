from datetime import date, datetime

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin


class InventoryHeaderModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "inventories"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")  # open, completed, cancelled
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    items = relationship("InventoryItemModel", back_populates="inventory", cascade="all, delete-orphan",
                         lazy="selectin")
