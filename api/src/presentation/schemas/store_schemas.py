from uuid import UUID

from pydantic import BaseModel, Field


class CreateStoreRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class UpdateStoreRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class StoreResponse(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}
