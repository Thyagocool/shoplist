from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic SQLAlchemy repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self.session = session
        self.model_class = model_class

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def find_by_id(self, id: UUID) -> T | None:
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def find_all(self, **filters: Any) -> list[T]:
        query = select(self.model_class)
        if filters:
            for key, value in filters.items():
                column = getattr(self.model_class, key, None)
                if column is not None:
                    query = query.where(column == value)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete(self, id: UUID) -> None:
        entity = await self.find_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
