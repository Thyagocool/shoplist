from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel


class CancelInventoryUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, inventory_id: UUID, user_id: UUID) -> None:
        header = await self.session.get(InventoryHeaderModel, inventory_id)
        if not header or str(header.user_id) != str(user_id):
            raise ValueError("Inventory not found")

        if header.status != "open":
            raise ValueError("Inventory is already completed or cancelled")

        header.status = "cancelled"
        await self.session.flush()
