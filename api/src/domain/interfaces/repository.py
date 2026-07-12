from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Generic repository interface following DIP (Dependency Inversion).
    
    Domain layer depends on this abstraction, not on infrastructure.
    """

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist an entity (insert or update)."""
        ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> T | None:
        """Find an entity by its ID."""
        ...

    @abstractmethod
    async def find_all(self, **filters) -> list[T]:
        """Find all entities matching optional filters."""
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete an entity by its ID."""
        ...
