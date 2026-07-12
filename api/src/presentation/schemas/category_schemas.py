from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(max_length=80)


class CategoryUpdateRequest(BaseModel):
    name: str = Field(max_length=80)


class CategoryResponse(BaseModel):
    id: str
    name: str
