from datetime import date as date_type
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryItemRequest(BaseModel):
    pre_registered_item_id: UUID
    declared_quantity: Decimal = Field(default=Decimal("0"), ge=0)


class InventoryItemResponse(BaseModel):
    id: UUID
    pre_registered_item_id: UUID
    item_name: str
    category_name: str
    declared_quantity: float
    previous_quantity: float
    default_unit: str

    model_config = {"from_attributes": True}


class CreateInventoryRequest(BaseModel):
    date: date_type | None = None
    notes: str | None = None
    items: list[InventoryItemRequest] = []


class InventorySummaryResponse(BaseModel):
    id: UUID
    date: date_type
    status: str
    notes: str | None
    item_count: int
    created_at: str

    model_config = {"from_attributes": True}


class InventoryDetailResponse(BaseModel):
    id: UUID
    date: date_type
    status: str
    notes: str | None
    items: list[InventoryItemResponse]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class UpdateInventoryItemsRequest(BaseModel):
    items: list[InventoryItemRequest]


# --- Old schemas kept for backward compat ---
class DeclareInventoryRequest(BaseModel):
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: Decimal = Field(default=Decimal("0"), ge=0)


class InventoryResponseOld(BaseModel):
    id: UUID
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    item_name: str = ""
    declared_quantity: float
    calculated_need: float

    model_config = {"from_attributes": True}
