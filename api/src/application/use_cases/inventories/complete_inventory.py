from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel
from src.infrastructure.database.models.stock_model import StockModel


class CompleteInventoryUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, inventory_id: UUID, user_id: UUID) -> None:
        header = await self.session.get(InventoryHeaderModel, inventory_id)
        if not header or str(header.user_id) != str(user_id):
            raise ValueError("Inventory not found")

        if header.status != "open":
            raise ValueError("Inventory is already completed or cancelled")

        items = await self.session.execute(
            select(InventoryItemModel).where(InventoryItemModel.inventory_id == inventory_id)
        )
        inventory_items = items.scalars().all()

        for inv_item in inventory_items:
            # Upsert stock
            result = await self.session.execute(
                select(StockModel).where(
                    StockModel.pre_registered_item_id == inv_item.pre_registered_item_id,
                    StockModel.user_id == user_id,
                )
            )
            stock = result.scalar_one_or_none()

            if stock:
                stock.current_quantity = float(inv_item.declared_quantity)
            else:
                stock = StockModel(
                    pre_registered_item_id=inv_item.pre_registered_item_id,
                    current_quantity=float(inv_item.declared_quantity),
                    user_id=user_id,
                )
                self.session.add(stock)

        header.status = "completed"
        await self.session.flush()
