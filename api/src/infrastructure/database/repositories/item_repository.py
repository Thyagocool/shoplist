from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository[ItemModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ItemModel)

    async def find_by_id(self, id: UUID) -> ItemModel | None:
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.id == id)
            .options(joinedload(ItemModel.category))
        )
        return result.scalar_one_or_none()

    async def find_active_by_user_id(self, user_id: UUID) -> list[ItemModel]:
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.user_id == user_id, ItemModel.active.is_(True))
            .options(joinedload(ItemModel.category))
            .order_by(ItemModel.name)
        )
        return list(result.scalars().all())

    async def find_by_category(self, category_id: UUID, user_id: UUID) -> list[ItemModel]:
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.category_id == category_id, ItemModel.user_id == user_id)
            .options(joinedload(ItemModel.category))
            .order_by(ItemModel.name)
        )
        return list(result.scalars().all())
