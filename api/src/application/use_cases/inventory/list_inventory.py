from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.application.dtos.inventory_dtos import InventoryOutput
from src.infrastructure.database.models.inventory_model import InventoryModel
from src.infrastructure.database.repositories.inventory_repository import InventoryRepository


class ListInventoryUseCase:
    def __init__(self, repo: InventoryRepository) -> None:
        self.repo = repo

    async def execute(self, shopping_list_id: UUID, user_id: UUID) -> list[InventoryOutput]:
        models = await self.repo.find_by_list_id(shopping_list_id)
        results = []
        for m in models:
            if str(m.user_id) != str(user_id):
                continue
            # Load item name
            from src.infrastructure.database.models.item_model import ItemModel

            result = await self.repo.session.execute(
                select(ItemModel).where(ItemModel.id == m.pre_registered_item_id)
            )
            item = result.scalar_one_or_none()
            results.append(
                InventoryOutput(
                    id=m.id,
                    shopping_list_id=m.shopping_list_id,
                    pre_registered_item_id=m.pre_registered_item_id,
                    declared_quantity=m.declared_quantity,
                    calculated_need=m.calculated_need,
                    item_name=item.name if item else "",
                )
            )
        return results
