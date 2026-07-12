from uuid import UUID

from sqlalchemy import select

from src.application.dtos.shopping_list_dtos import AddListItemInput, ListItemOutput
from src.domain.entities.shopping_list_item import ShoppingListItem
from src.domain.value_objects.unit import Unit
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.list_item_model import ShoppingListItemModel
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class AddListItemUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, input_data: AddListItemInput) -> ListItemOutput:
        # Validate list belongs to user
        list_model = await self.repo.find_by_id(input_data.shopping_list_id)
        if not list_model or str(list_model.user_id) != str(input_data.user_id):
            raise ValueError("Shopping list not found")
        if list_model.status not in ("pending", "in_progress"):
            raise ValueError("Cannot modify completed/cancelled list")

        unit = Unit(input_data.unit) if input_data.unit else Unit.UN
        item_name = ""

        if input_data.pre_registered_item_id:
            entity = ShoppingListItem.from_pre_registered(
                shopping_list_id=input_data.shopping_list_id,
                pre_registered_item_id=input_data.pre_registered_item_id,
                estimated_quantity=input_data.estimated_quantity,
                unit=unit,
                user_id=input_data.user_id,
            )
            # Get item name
            result = await self.repo.session.execute(
                select(ItemModel).where(ItemModel.id == input_data.pre_registered_item_id)
            )
            item_model = result.scalar_one_or_none()
            item_name = item_model.name if item_model else ""
        else:
            entity = ShoppingListItem.create_custom(
                shopping_list_id=input_data.shopping_list_id,
                name=input_data.custom_name or "",
                quantity=input_data.estimated_quantity,
                unit=unit,
                user_id=input_data.user_id,
            )
            item_name = input_data.custom_name or ""

        model = ShoppingListItemModel(
            id=entity.id,
            shopping_list_id=entity.shopping_list_id,
            pre_registered_item_id=entity.pre_registered_item_id,
            custom_name=entity.custom_name,
            estimated_quantity=float(entity.estimated_quantity),
            unit=entity.unit.value,
            checked=entity.checked,
            store_id=input_data.store_id,
            user_id=entity.user_id,
        )
        self.repo.session.add(model)
        await self.uow.commit()

        return ListItemOutput(
            id=model.id,
            pre_registered_item_id=model.pre_registered_item_id,
            custom_name=model.custom_name,
            estimated_quantity=model.estimated_quantity,
            unit=model.unit,
            checked=model.checked,
            price_cents=model.price_cents,
            item_name=item_name,
        )
