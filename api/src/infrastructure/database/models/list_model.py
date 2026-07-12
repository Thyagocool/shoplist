from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin


class ShoppingListModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "shopping_lists"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("UserModel", back_populates="shopping_lists")
    items = relationship("ShoppingListItemModel", back_populates="shopping_list", lazy="selectin", cascade="all, delete-orphan")
    inventory_declarations = relationship("InventoryModel", back_populates="shopping_list", lazy="selectin")
