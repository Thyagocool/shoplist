from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class StockRepository(BaseRepository[StockModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StockModel)

    async def find_by_item_id(self, item_id: UUID) -> StockModel | None:
        result = await self.session.execute(
            select(StockModel).where(StockModel.pre_registered_item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def find_by_user_id(self, user_id: UUID) -> list[StockModel]:
        result = await self.session.execute(
            select(StockModel)
            .where(StockModel.user_id == user_id)
            .options(joinedload(StockModel.item))
            .order_by(StockModel.updated_at.desc())
        )
        return list(result.scalars().all())

    async def find_alerts(self, user_id: UUID) -> list[StockModel]:
        """Find stock entries where current_quantity < item.min_stock."""
        result = await self.session.execute(
            select(StockModel)
            .join(ItemModel)
            .where(
                StockModel.user_id == user_id,
                StockModel.current_quantity < ItemModel.min_stock,
            )
            .options(joinedload(StockModel.item))
        )
        return list(result.scalars().all())
