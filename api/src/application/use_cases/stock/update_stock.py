from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.stock_dtos import UpdateStockInput, UpdateStockOutput
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel


class UpdateStockUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, input_data: UpdateStockInput) -> UpdateStockOutput:
        """Upsert the current stock quantity for an item."""
        item = await self.session.get(ItemModel, input_data.pre_registered_item_id)
        if not item or str(item.user_id) != str(input_data.user_id):
            raise ValueError("Item not found")

        result = await self.session.execute(
            select(StockModel).where(
                StockModel.pre_registered_item_id == input_data.pre_registered_item_id,
                StockModel.user_id == input_data.user_id,
            )
        )
        stock = result.scalar_one_or_none()

        if stock:
            stock.current_quantity = float(input_data.current_quantity)
        else:
            stock = StockModel(
                pre_registered_item_id=input_data.pre_registered_item_id,
                current_quantity=float(input_data.current_quantity),
                user_id=input_data.user_id,
            )
            self.session.add(stock)

        await self.session.commit()

        return UpdateStockOutput(
            pre_registered_item_id=input_data.pre_registered_item_id,
            current_quantity=input_data.current_quantity,
        )


class BatchUpdateStockUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self, items: list[UpdateStockInput]
    ) -> list[UpdateStockOutput]:
        results: list[UpdateStockOutput] = []
        for inp in items:
            item = await self.session.get(ItemModel, inp.pre_registered_item_id)
            if not item or str(item.user_id) != str(inp.user_id):
                continue

            result = await self.session.execute(
                select(StockModel).where(
                    StockModel.pre_registered_item_id == inp.pre_registered_item_id,
                    StockModel.user_id == inp.user_id,
                )
            )
            stock = result.scalar_one_or_none()

            if stock:
                stock.current_quantity = float(inp.current_quantity)
            else:
                stock = StockModel(
                    pre_registered_item_id=inp.pre_registered_item_id,
                    current_quantity=float(inp.current_quantity),
                    user_id=inp.user_id,
                )
                self.session.add(stock)

        await self.session.commit()

        return [
            UpdateStockOutput(
                pre_registered_item_id=inp.pre_registered_item_id,
                current_quantity=inp.current_quantity,
            )
            for inp in items
        ]
