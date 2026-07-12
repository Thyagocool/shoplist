from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.inventory_model import InventoryModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[InventoryModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, InventoryModel)

    async def find_by_list_id(self, shopping_list_id: UUID) -> list[InventoryModel]:
        result = await self.session.execute(
            select(InventoryModel).where(InventoryModel.shopping_list_id == shopping_list_id)
        )
        return list(result.scalars().all())
