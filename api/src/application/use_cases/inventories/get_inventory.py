from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.application.dtos.inventory_dtos import InventoryDetailOutput, InventoryItemOutput
from src.infrastructure.database.models.inventory_header_model import InventoryHeaderModel
from src.infrastructure.database.models.inventory_item_model import InventoryItemModel
from src.infrastructure.database.models.item_model import ItemModel


class GetInventoryUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, inventory_id: UUID, user_id: UUID) -> InventoryDetailOutput | None:
        header = await self.session.get(InventoryHeaderModel, inventory_id)
        if not header or str(header.user_id) != str(user_id):
            return None

        # Fetch items with item + category eager-loaded
        items_result = await self.session.execute(
            select(InventoryItemModel)
            .where(InventoryItemModel.inventory_id == inventory_id)
            .options(
                joinedload(InventoryItemModel.item).joinedload(ItemModel.category)
            )
        )
        inventory_items = items_result.unique().scalars().all()

        items_out = []
        for inv_item in inventory_items:
            item_model = inv_item.item
            category_name = "Sem categoria"
            if item_model and item_model.category:
                category_name = item_model.category.name

            items_out.append(
                InventoryItemOutput(
                    id=inv_item.id,
                    pre_registered_item_id=inv_item.pre_registered_item_id,
                    item_name=item_model.name if item_model else "Item removido",
                    category_name=category_name,
                    declared_quantity=float(inv_item.declared_quantity),
                    previous_quantity=float(inv_item.previous_quantity),
                    default_unit=item_model.default_unit if item_model else "un",
                )
            )

        # Sort by category then name
        items_out.sort(key=lambda x: (x.category_name, x.item_name))

        return InventoryDetailOutput(
            id=header.id,
            date=header.date,
            status=header.status,
            notes=header.notes,
            items=items_out,
            created_at=header.created_at.isoformat(),
            updated_at=header.updated_at.isoformat(),
        )
