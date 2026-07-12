from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from src.application.dtos.shopping_list_dtos import ListItemOutput
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.list_item_model import ShoppingListItemModel
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class UpdateListItemUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(
        self,
        item_id: UUID,
        user_id: UUID,
        unit: str | None = None,
        estimated_quantity: Decimal | None = None,
    ) -> ListItemOutput | None:
        result = await self.repo.session.execute(
            select(ShoppingListItemModel)
            .where(ShoppingListItemModel.id == item_id)
        )
        model = result.scalar_one_or_none()
        if not model or str(model.user_id) != str(user_id):
            return None

        # Check list is not completed
        list_model = await self.repo.find_by_id(model.shopping_list_id)
        if list_model and list_model.status not in ("pending", "in_progress"):
            raise ValueError("Cannot modify completed/cancelled list")

        if unit is not None:
            model.unit = unit
        if estimated_quantity is not None:
            model.estimated_quantity = float(estimated_quantity)

        await self.repo.session.flush()
        await self.uow.commit()

        item_name = ""
        if model.pre_registered_item_id:
            item_result = await self.repo.session.execute(
                select(ItemModel).where(ItemModel.id == model.pre_registered_item_id)
            )
            item_model = item_result.scalar_one_or_none()
            item_name = item_model.name if item_model else ""
        elif model.custom_name:
            item_name = model.custom_name

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
