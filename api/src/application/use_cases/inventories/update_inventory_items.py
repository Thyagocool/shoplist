from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.dtos.inventory_dtos import (
    InventoryDetailOutput,
    InventoryItemInput,
    InventoryItemOutput,
)
from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel


class UpdateInventoryItemsUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self, inventory_id: UUID, items: list[InventoryItemInput], user_id: UUID
    ) -> InventoryDetailOutput | None:
        header = await self.session.get(InventoryHeaderModel, inventory_id)
        if not header or str(header.user_id) != str(user_id):
            return None

        if header.status != "open":
            raise ValueError("Cannot modify a completed inventory")

        existing_items = await self.session.execute(
            select(InventoryItemModel).where(InventoryItemModel.inventory_id == inventory_id)
        )
        existing_map = {
            str(item.pre_registered_item_id): item
            for item in existing_items.scalars().all()
        }

        items_out: list[InventoryItemOutput] = []
        for item_in in items:
            item_id_str = str(item_in.pre_registered_item_id)
            if item_id_str in existing_map:
                # Update existing
                inv_item = existing_map[item_id_str]
                inv_item.declared_quantity = float(item_in.declared_quantity)
            else:
                # Get stock for new item
                result = await self.session.execute(
                    select(StockModel).where(
                        StockModel.pre_registered_item_id == item_in.pre_registered_item_id,
                        StockModel.user_id == user_id,
                    )
                )
                stock = result.scalar_one_or_none()
                previous_qty = float(stock.current_quantity) if stock else 0

                inv_item = InventoryItemModel(
                    id=uuid4(),
                    inventory_id=inventory_id,
                    pre_registered_item_id=item_in.pre_registered_item_id,
                    declared_quantity=float(item_in.declared_quantity),
                    previous_quantity=previous_qty,
                )
                self.session.add(inv_item)

            # Load item info with category
            item_result = await self.session.execute(
                select(ItemModel)
                .where(ItemModel.id == item_in.pre_registered_item_id)
                .options(joinedload(ItemModel.category))
            )
            item_model = item_result.unique().scalar_one_or_none()

            items_out.append(
                InventoryItemOutput(
                    id=inv_item.id,
                    pre_registered_item_id=item_in.pre_registered_item_id,
                    item_name=item_model.name if item_model else "Item removido",
                    category_name=item_model.category.name if item_model and item_model.category else "Sem categoria",
                    declared_quantity=float(item_in.declared_quantity),
                    previous_quantity=float(inv_item.previous_quantity),
                    default_unit=item_model.default_unit if item_model else "un",
                )
            )

        await self.session.flush()

        # Re-fetch to get all items
        from src.application.use_cases.inventories.get_inventory import GetInventoryUseCase
        getter = GetInventoryUseCase(self.session)
        return await getter.execute(inventory_id, user_id)
