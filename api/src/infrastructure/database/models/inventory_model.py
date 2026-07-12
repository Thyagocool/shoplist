from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class InventoryModel(UUIDMixin, Base):
    __tablename__ = "inventory_declarations"

    shopping_list_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shopping_lists.id"), nullable=False)
    pre_registered_item_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pre_registered_items.id"), nullable=False)
    declared_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    calculated_need: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    shopping_list = relationship("ShoppingListModel", back_populates="inventory_declarations")
    user = relationship("UserModel", back_populates="inventory_declarations")
