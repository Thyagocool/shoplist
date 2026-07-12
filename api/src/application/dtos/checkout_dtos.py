from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class CheckoutItemInput:
    shopping_list_item_id: UUID
    price_cents: int = 0
    store_id: UUID | None = None


@dataclass
class CheckoutInput:
    shopping_list_id: UUID
    user_id: UUID
    items: list[CheckoutItemInput] = field(default_factory=list)


@dataclass
class MovementOutput:
    id: UUID
    sequential_code: str
    item_name: str
    quantity: float
    unit: str
    price_cents: int
    store_name: str | None


@dataclass
class CheckoutOutput:
    movements: list[MovementOutput] = field(default_factory=list)
    list_status: str = ""
