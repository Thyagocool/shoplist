from uuid import UUID

from pydantic import BaseModel, Field


class CheckoutItemRequest(BaseModel):
    shopping_list_item_id: UUID
    price_cents: int = Field(default=0, ge=0)
    store_id: UUID | None = None


class CheckoutRequest(BaseModel):
    items: list[CheckoutItemRequest] = []


class MovementResponse(BaseModel):
    id: UUID
    sequential_code: str
    item_name: str
    quantity: float
    unit: str
    price_cents: int
    store_name: str | None = None

    model_config = {"from_attributes": True}


class CheckoutResponse(BaseModel):
    movements: list[MovementResponse] = []
    list_status: str
