from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateCategoryInput:
    name: str
    user_id: UUID


@dataclass
class UpdateCategoryInput:
    name: str


@dataclass
class CategoryOutput:
    id: UUID
    name: str
