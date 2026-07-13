from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.dtos.stock_dtos import StockOutput
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel


class ListStockUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, user_id: UUID) -> list[StockOutput]:
        """Return current stock for all active items of the user.
        Items without a stock entry will appear with quantity 0."""
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.user_id == user_id, ItemModel.active == True)  # noqa: E712
            .options(joinedload(ItemModel.stock), joinedload(ItemModel.category))
            .order_by(ItemModel.name)
        )
        items = result.unique().scalars().all()

        output: list[StockOutput] = []
        for item in items:
            qty = item.stock.current_quantity if item.stock else 0
            output.append(
                StockOutput(
                    pre_registered_item_id=item.id,
                    item_name=item.name,
                    category_name=item.category.name if item.category else "Sem categoria",
                    current_quantity=float(qty) if qty else 0,
                    default_unit=item.default_unit,
                    min_stock=float(item.min_stock) if item.min_stock else 0,
                    max_stock=float(item.max_stock) if item.max_stock else 0,
                )
            )
        return output
