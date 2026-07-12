from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class StockModel(UUIDMixin, Base):
    __tablename__ = "stock"

    pre_registered_item_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pre_registered_items.id"), unique=True, nullable=False
    )
    current_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    last_price_cents: Mapped[int | None] = mapped_column(nullable=True)
    last_store_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    item = relationship("ItemModel", back_populates="stock")
    user = relationship("UserModel", back_populates="stock_entries")
