from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CreateItemInput:
    name: str
    category_id: UUID
    user_id: UUID
    default_unit: str = "un"
    default_quantity: Decimal = Decimal("1")
    min_stock: Decimal = Decimal("0")
    max_stock: Decimal = Decimal("0")


@dataclass
class UpdateItemInput:
    name: str | None = None
    category_id: UUID | None = None
    default_unit: str | None = None
    default_quantity: Decimal | None = None
    min_stock: Decimal | None = None
    max_stock: Decimal | None = None


@dataclass
class ItemOutput:
    id: UUID
    name: str
    category_id: UUID
    default_unit: str
    default_quantity: Decimal
    min_stock: Decimal
    max_stock: Decimal
    active: bool
    category_name: str = ""
