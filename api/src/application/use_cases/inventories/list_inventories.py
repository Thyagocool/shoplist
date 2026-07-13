from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.inventory_dtos import InventoryOutput
from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel


class ListInventoriesUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, user_id: UUID) -> list[InventoryOutput]:
        # Get inventory count per header
        subq = (
            select(
                InventoryItemModel.inventory_id,
                func.count(InventoryItemModel.id).label("item_count"),
            )
            .group_by(InventoryItemModel.inventory_id)
            .subquery()
        )

        result = await self.session.execute(
            select(
                InventoryHeaderModel,
                func.coalesce(subq.c.item_count, 0).label("item_count"),
            )
            .outerjoin(subq, InventoryHeaderModel.id == subq.c.inventory_id)
            .where(InventoryHeaderModel.user_id == user_id)
            .order_by(InventoryHeaderModel.created_at.desc())
        )

        rows = result.all()
        return [
            InventoryOutput(
                id=header.id,
                date=header.date,
                status=header.status,
                notes=header.notes,
                item_count=item_count,
                created_at=header.created_at.isoformat(),
            )
            for header, item_count in rows
        ]
