from abc import ABC, abstractmethod
from uuid import UUID


class AuthService(ABC):
    """Authentication service interface.
    
    Handles password hashing and JWT token management.
    """

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        ...

    @abstractmethod
    async def verify_password(self, password: str, password_hash: str) -> bool:
        ...

    @abstractmethod
    def create_access_token(self, user_id: UUID) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        ...
