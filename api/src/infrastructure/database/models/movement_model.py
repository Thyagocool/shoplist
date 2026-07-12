from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class MovementModel(UUIDMixin, Base):
    __tablename__ = "movements"

    sequential_code: Mapped[str] = mapped_column(String(20), nullable=False)
    shopping_list_item_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("shopping_list_items.id"), nullable=True)
    pre_registered_item_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pre_registered_items.id"), nullable=True)
    custom_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    store_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    store_name_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="movements")
    store = relationship("StoreModel", back_populates="movements")
