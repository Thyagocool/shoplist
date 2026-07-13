from uuid import UUID

from src.application.dtos.shopping_list_dtos import ListItemOutput, ShoppingListOutput
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository


class GetShoppingListUseCase:
    def __init__(self, repo: ShoppingListRepository) -> None:
        self.repo = repo

    async def execute(self, list_id: UUID, user_id: UUID) -> ShoppingListOutput | None:
        model = await self.repo.find_with_items(list_id)
        if not model or str(model.user_id) != str(user_id):
            return None

        items = []
        for item in model.items:
            item_name = item.custom_name or ""
            if item.pre_registered_item_id and not item_name:
                from sqlalchemy import select
                from src.infrastructure.database.models.item_model import ItemModel

                result = await self.repo.session.execute(
                    select(ItemModel).where(ItemModel.id == item.pre_registered_item_id)
                )
                item_model = result.scalar_one_or_none()
                item_name = item_model.name if item_model else ""

            items.append(
                ListItemOutput(
                    id=item.id,
                    pre_registered_item_id=item.pre_registered_item_id,
                    custom_name=item.custom_name,
                    estimated_quantity=item.estimated_quantity,
                    unit=item.unit,
                    checked=item.checked,
                    price_cents=item.price_cents,
                    item_name=item_name,
                )
            )

        return ShoppingListOutput(
            id=model.id,
            name=model.name,
            status=model.status,
            store_id=model.store_id,
            store_name=model.store.name if model.store else None,
            completed_at=model.completed_at,
            items=items,
        )
