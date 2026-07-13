from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class CreateShoppingListInput:
    name: str
    user_id: UUID
    store_id: UUID | None = None


@dataclass
class AddListItemInput:
    shopping_list_id: UUID
    user_id: UUID
    pre_registered_item_id: UUID | None = None
    custom_name: str | None = None
    estimated_quantity: Decimal = Decimal("1")
    unit: str = "un"
    store_id: UUID | None = None


@dataclass
class ListItemOutput:
    id: UUID
    pre_registered_item_id: UUID | None
    custom_name: str | None
    estimated_quantity: float
    unit: str
    checked: bool
    price_cents: int | None
    item_name: str = ""


@dataclass
class ShoppingListOutput:
    id: UUID
    name: str
    status: str
    store_id: UUID | None = None
    store_name: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    items: list[ListItemOutput] = field(default_factory=list)
