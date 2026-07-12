from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin


class ItemModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "pre_registered_items"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    default_unit: Mapped[str] = mapped_column(String(20), nullable=False, default="un")
    default_quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=1.0)
    min_stock: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    max_stock: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    user = relationship("UserModel", back_populates="items")
    category = relationship("CategoryModel", back_populates="items")
    stock = relationship("StockModel", back_populates="item", uselist=False, lazy="selectin")
