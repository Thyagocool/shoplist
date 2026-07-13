from uuid import UUID

from src.application.dtos.shopping_list_dtos import ListItemOutput, ShoppingListOutput
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository


class ListShoppingListsUseCase:
    def __init__(self, repo: ShoppingListRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID) -> list[ShoppingListOutput]:
        models = await self.repo.find_by_user_id(user_id)
        return [
            ShoppingListOutput(
                id=m.id,
                name=m.name,
                status=m.status,
                store_id=m.store_id,
                store_name=m.store.name if m.store else None,
                completed_at=m.completed_at,
                items=[
                    ListItemOutput(
                        id=i.id,
                        pre_registered_item_id=i.pre_registered_item_id,
                        custom_name=i.custom_name,
                        estimated_quantity=i.estimated_quantity,
                        unit=i.unit,
                        checked=i.checked,
                        price_cents=i.price_cents,
                        item_name=i.custom_name or "",
                    )
                    for i in m.items
                ],
            )
            for m in models
        ]
