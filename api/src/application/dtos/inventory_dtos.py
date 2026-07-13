from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class InventoryItemInput:
    pre_registered_item_id: UUID
    declared_quantity: Decimal


@dataclass
class InventoryItemOutput:
    id: UUID
    pre_registered_item_id: UUID
    item_name: str
    category_name: str
    declared_quantity: float
    previous_quantity: float
    default_unit: str


@dataclass
class CreateInventoryInput:
    date: date
    notes: str | None
    items: list[InventoryItemInput]
    user_id: UUID


@dataclass
class InventoryOutput:
    id: UUID
    date: date
    status: str
    notes: str | None
    item_count: int
    created_at: str


@dataclass
class InventoryDetailOutput:
    id: UUID
    date: date
    status: str
    notes: str | None
    items: list[InventoryItemOutput]
    created_at: str
    updated_at: str


@dataclass
class UpdateInventoryItemsInput:
    inventory_id: UUID
    items: list[InventoryItemInput]
    user_id: UUID


# --- Old DTOs kept for backward compat ---
@dataclass
class DeclareInventoryInput:
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: Decimal
    user_id: UUID


@dataclass
class InventoryOutputOld:
    id: UUID
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: float
    calculated_need: float
    item_name: str = ""
