from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class DeclareInventoryRequest(BaseModel):
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    declared_quantity: Decimal = Field(default=Decimal("0"), ge=0)


class InventoryResponse(BaseModel):
    id: UUID
    shopping_list_id: UUID
    pre_registered_item_id: UUID
    item_name: str = ""
    declared_quantity: float
    calculated_need: float

    model_config = {"from_attributes": True}
