from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateShoppingListRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    store_id: UUID | None = None


class AddListItemRequest(BaseModel):
    pre_registered_item_id: UUID | None = None
    custom_name: str | None = Field(None, max_length=120)
    estimated_quantity: Decimal = Decimal("1")
    unit: str = "un"
    store_id: UUID | None = None


class UpdateListItemRequest(BaseModel):
    unit: str | None = None
    estimated_quantity: Decimal | None = None
    price_cents: int | None = None


class ListItemResponse(BaseModel):
    id: UUID
    pre_registered_item_id: UUID | None = None
    custom_name: str | None = None
    item_name: str = ""
    estimated_quantity: float
    unit: str
    checked: bool
    price_cents: int | None = None

    model_config = {"from_attributes": True}


class ShoppingListResponse(BaseModel):
    id: UUID
    name: str
    status: str
    store_id: UUID | None = None
    store_name: str | None = None
    completed_at: datetime | None = None
    items: list[ListItemResponse] = []

    model_config = {"from_attributes": True}
