from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.dtos.inventory_dtos import (
    CreateInventoryInput,
    InventoryDetailOutput,
    InventoryItemOutput,
)
from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel


class CreateInventoryUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, input_data: CreateInventoryInput) -> InventoryDetailOutput:
        header = InventoryHeaderModel(
            id=uuid4(),
            user_id=input_data.user_id,
            date=input_data.date,
            notes=input_data.notes,
            status="open",
        )
        self.session.add(header)

        items_out: list[InventoryItemOutput] = []
        for item_in in input_data.items:
            # Get current stock
            result = await self.session.execute(
                select(StockModel).where(
                    StockModel.pre_registered_item_id == item_in.pre_registered_item_id,
                    StockModel.user_id == input_data.user_id,
                )
            )
            stock = result.scalar_one_or_none()
            previous_qty = float(stock.current_quantity) if stock else 0

            # Get item info with category loaded
            item_result = await self.session.execute(
                select(ItemModel)
                .where(ItemModel.id == item_in.pre_registered_item_id)
                .options(joinedload(ItemModel.category))
            )
            item_model = item_result.unique().scalar_one_or_none()

            inv_item = InventoryItemModel(
                id=uuid4(),
                inventory_id=header.id,
                pre_registered_item_id=item_in.pre_registered_item_id,
                declared_quantity=float(item_in.declared_quantity),
                previous_quantity=previous_qty,
            )
            self.session.add(inv_item)

            items_out.append(
                InventoryItemOutput(
                    id=inv_item.id,
                    pre_registered_item_id=item_in.pre_registered_item_id,
                    item_name=item_model.name if item_model else "Item removido",
                    category_name=item_model.category.name if item_model and item_model.category else "Sem categoria",
                    declared_quantity=float(item_in.declared_quantity),
                    previous_quantity=previous_qty,
                    default_unit=item_model.default_unit if item_model else "un",
                )
            )

        await self.session.flush()

        return InventoryDetailOutput(
            id=header.id,
            date=input_data.date,
            status="open",
            notes=input_data.notes,
            items=items_out,
            created_at=header.created_at.isoformat(),
            updated_at=header.updated_at.isoformat(),
        )
