from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category_id: UUID
    default_unit: str = "un"
    default_quantity: Decimal = Decimal("1")
    min_stock: Decimal = Decimal("0")
    max_stock: Decimal = Decimal("0")


class UpdateItemRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    category_id: UUID | None = None
    default_unit: str | None = None
    default_quantity: Decimal | None = None
    min_stock: Decimal | None = None
    max_stock: Decimal | None = None


class ItemResponse(BaseModel):
    id: UUID
    name: str
    category_id: UUID
    default_unit: str
    default_quantity: float
    min_stock: float
    max_stock: float
    active: bool
    category_name: str = ""

    model_config = {"from_attributes": True}
