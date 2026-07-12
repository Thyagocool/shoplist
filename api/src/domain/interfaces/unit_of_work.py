from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Unit of Work pattern interface.
    
    Ensures all repository operations are committed atomically.
    """

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        ...

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        ...

    @abstractmethod
    async def __aexit__(self, *args: object) -> None:
        ...
