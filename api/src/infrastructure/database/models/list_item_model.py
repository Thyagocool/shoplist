from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class ShoppingListItemModel(UUIDMixin, Base):
    __tablename__ = "shopping_list_items"

    shopping_list_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shopping_lists.id"), nullable=False)
    pre_registered_item_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pre_registered_items.id"), nullable=True)
    custom_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estimated_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=1.0)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="un")
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_cents: Mapped[int | None] = mapped_column(nullable=True)
    store_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(nullable=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    shopping_list = relationship("ShoppingListModel", back_populates="items")
    user = relationship("UserModel")
