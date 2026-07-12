from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.store_model import StoreModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class StoreRepository(BaseRepository[StoreModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StoreModel)

    async def find_by_user_id(self, user_id: UUID) -> list[StoreModel]:
        result = await self.session.execute(
            select(StoreModel).where(StoreModel.user_id == user_id).order_by(StoreModel.name)
        )
        return list(result.scalars().all())

    async def find_by_name(self, name: str, user_id: UUID) -> StoreModel | None:
        result = await self.session.execute(
            select(StoreModel).where(StoreModel.name == name, StoreModel.user_id == user_id)
        )
        return result.scalar_one_or_none()
