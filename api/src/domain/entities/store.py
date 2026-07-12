from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Store:
    """A store/market where the user shops."""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    user_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, name: str, user_id: UUID) -> "Store":
        return cls(
            id=uuid4(),
            name=name,
            user_id=user_id,
            created_at=datetime.now(),
        )
