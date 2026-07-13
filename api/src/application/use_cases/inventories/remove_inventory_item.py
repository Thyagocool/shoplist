from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel


class RemoveInventoryItemUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, inventory_id: UUID, item_id: UUID, user_id: UUID) -> None:
        header = await self.session.get(InventoryHeaderModel, inventory_id)
        if not header or str(header.user_id) != str(user_id):
            raise ValueError("Inventory not found")

        if header.status != "open":
            raise ValueError("Cannot modify a completed inventory")

        item = await self.session.get(InventoryItemModel, item_id)
        if not item or str(item.inventory_id) != str(inventory_id):
            raise ValueError("Item not found in inventory")

        await self.session.delete(item)
        await self.session.flush()
