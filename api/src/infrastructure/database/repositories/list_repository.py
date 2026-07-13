from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.database.models.list_model import ShoppingListModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class ShoppingListRepository(BaseRepository[ShoppingListModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ShoppingListModel)

    async def find_by_user_id(self, user_id: UUID) -> list[ShoppingListModel]:
        result = await self.session.execute(
            select(ShoppingListModel)
            .where(ShoppingListModel.user_id == user_id)
            .order_by(ShoppingListModel.created_at.desc())
            .options(joinedload(ShoppingListModel.store))
        )
        return list(result.scalars().unique().all())

    async def find_with_items(self, list_id: UUID) -> ShoppingListModel | None:
        result = await self.session.execute(
            select(ShoppingListModel)
            .where(ShoppingListModel.id == list_id)
            .options(
                joinedload(ShoppingListModel.items),
                joinedload(ShoppingListModel.inventory_declarations),
                joinedload(ShoppingListModel.store),
            )
        )
        return result.unique().scalar_one_or_none()

    async def find_in_progress(self, user_id: UUID) -> ShoppingListModel | None:
        result = await self.session.execute(
            select(ShoppingListModel)
            .where(
                ShoppingListModel.user_id == user_id,
                ShoppingListModel.status.in_(["pending", "in_progress"]),
            )
            .order_by(ShoppingListModel.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def delete_item(self, item_id: UUID) -> bool:
        """Remove um item da lista de compras."""
        from src.infrastructure.database.models.list_item_model import ShoppingListItemModel

        result = await self.session.execute(
            select(ShoppingListItemModel).where(ShoppingListItemModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True
