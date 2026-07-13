from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class InventoryItemModel(UUIDMixin, Base):
    __tablename__ = "inventory_items"

    inventory_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False
    )
    pre_registered_item_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pre_registered_items.id"), nullable=False
    )
    declared_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    previous_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    # Relationships
    inventory = relationship("InventoryHeaderModel", back_populates="items")
    item = relationship("ItemModel", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("inventory_id", "pre_registered_item_id", name="uq_inventory_item"),
    )
