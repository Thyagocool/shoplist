from uuid import UUID

from src.application.dtos.item_dtos import ItemOutput
from src.infrastructure.database.repositories.item_repository import ItemRepository


class ListItemsUseCase:
    def __init__(self, repo: ItemRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID) -> list[ItemOutput]:
        models = await self.repo.find_active_by_user_id(user_id)
        items = []
        for m in models:
            items.append(
                ItemOutput(
                    id=m.id,
                    name=m.name,
                    category_id=m.category_id,
                    category_name=m.category.name if m.category else "",
                    default_unit=m.default_unit,
                    default_quantity=m.default_quantity,
                    min_stock=m.min_stock,
                    max_stock=m.max_stock,
                    active=m.active,
                )
            )
        return items
