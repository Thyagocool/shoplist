from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class ShoppingListStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ShoppingList:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    status: ShoppingListStatus = ShoppingListStatus.PENDING
    user_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @classmethod
    def create(cls, name: str, user_id: UUID) -> "ShoppingList":
        return cls(
            id=uuid4(),
            name=name,
            status=ShoppingListStatus.IN_PROGRESS,
            user_id=user_id,
            created_at=datetime.now(),
        )

    def complete(self) -> None:
        self.status = ShoppingListStatus.COMPLETED
        self.completed_at = datetime.now()

    def cancel(self) -> None:
        self.status = ShoppingListStatus.CANCELLED
