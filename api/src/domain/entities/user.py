from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.value_objects.email import Email


@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    email: Email | None = None
    password_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, name: str, email: Email, password_hash: str) -> "User":
        now = datetime.now()
        return cls(
            id=uuid4(),
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=now,
            updated_at=now,
        )
