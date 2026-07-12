from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateStoreInput:
    name: str
    user_id: UUID


@dataclass
class UpdateStoreInput:
    name: str | None = None


@dataclass
class StoreOutput:
    id: UUID
    name: str
