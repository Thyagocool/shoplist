from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class DeclareInventoryInput:
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: Decimal
    user_id: UUID


@dataclass
class InventoryOutput:
    id: UUID
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: float
    calculated_need: float
    item_name: str = ""
