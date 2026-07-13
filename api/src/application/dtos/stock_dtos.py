from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class StockOutput:
    pre_registered_item_id: UUID
    item_name: str
    category_name: str
    current_quantity: Decimal
    default_unit: str
    min_stock: Decimal
    max_stock: Decimal


@dataclass
class UpdateStockInput:
    pre_registered_item_id: UUID
    current_quantity: Decimal
    user_id: UUID


@dataclass
class UpdateStockOutput:
    pre_registered_item_id: UUID
    current_quantity: Decimal
