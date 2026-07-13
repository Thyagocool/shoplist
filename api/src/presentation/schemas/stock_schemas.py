from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class StockResponse(BaseModel):
    pre_registered_item_id: UUID
    item_name: str
    category_name: str
    current_quantity: float
    default_unit: str
    min_stock: float
    max_stock: float

    model_config = {"from_attributes": True}


class UpdateStockRequest(BaseModel):
    pre_registered_item_id: UUID
    current_quantity: Decimal = Field(default=Decimal("0"), ge=0)


class UpdateStockResponse(BaseModel):
    pre_registered_item_id: UUID
    current_quantity: float

    model_config = {"from_attributes": True}


class BatchUpdateStockRequest(BaseModel):
    items: list[UpdateStockRequest]
