"""SQLAlchemy ORM models.

Import all models here so Alembic can detect them.
"""
from src.infrastructure.database.models.base import Base
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.store_model import StoreModel
from src.infrastructure.database.models.list_model import ShoppingListModel
from src.infrastructure.database.models.list_item_model import ShoppingListItemModel
from src.infrastructure.database.models.movement_model import MovementModel
from src.infrastructure.database.models.stock_model import StockModel
from src.infrastructure.database.models.inventory_model import InventoryModel
from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel

__all__ = [
    "Base",
    "UserModel",
    "CategoryModel",
    "ItemModel",
    "StoreModel",
    "ShoppingListModel",
    "ShoppingListItemModel",
    "MovementModel",
    "StockModel",
    "InventoryModel",
    "InventoryHeaderModel",
    "InventoryItemModel",
]
