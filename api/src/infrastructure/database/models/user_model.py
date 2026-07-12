from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin


class UserModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    categories = relationship("CategoryModel", back_populates="user", lazy="selectin")
    items = relationship("ItemModel", back_populates="user", lazy="selectin")
    stores = relationship("StoreModel", back_populates="user", lazy="selectin")
    shopping_lists = relationship("ShoppingListModel", back_populates="user", lazy="selectin")
    movements = relationship("MovementModel", back_populates="user", lazy="selectin")
    stock_entries = relationship("StockModel", back_populates="user", lazy="selectin")
    inventory_declarations = relationship("InventoryModel", back_populates="user", lazy="selectin")
