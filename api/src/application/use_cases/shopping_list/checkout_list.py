from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from src.application.dtos.checkout_dtos import CheckoutInput, CheckoutOutput, MovementOutput
from src.domain.entities.movement import Movement
from src.domain.value_objects.unit import Unit
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.list_item_model import ShoppingListItemModel
from src.infrastructure.database.models.list_model import ShoppingListModel
from src.infrastructure.database.models.movement_model import MovementModel
from src.infrastructure.database.models.stock_model import StockModel
from src.infrastructure.database.models.store_model import StoreModel
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.repositories.movement_repository import MovementRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from src.domain.entities.shopping_list import ShoppingListStatus


class CheckoutListUseCase:
    def __init__(
        self,
        list_repo: ShoppingListRepository,
        movement_repo: MovementRepository,
        uow: SQLAlchemyUnitOfWork,
    ) -> None:
        self.list_repo = list_repo
        self.movement_repo = movement_repo
        self.uow = uow

    async def execute(
        self,
        input_data: CheckoutInput,
    ) -> CheckoutOutput:
        from datetime import datetime, timezone

        # Get list
        list_model = await self.list_repo.find_by_id(input_data.shopping_list_id)
        if not list_model or str(list_model.user_id) != str(input_data.user_id):
            raise ValueError("Shopping list not found")
        if list_model.status not in ("pending", "in_progress"):
            raise ValueError("Shopping list already completed/cancelled")

        # Get list items (with relationships)
        result = await self.list_repo.session.execute(
            select(ShoppingListItemModel)
            .where(ShoppingListItemModel.shopping_list_id == input_data.shopping_list_id)
        )
        all_items = list(result.scalars().all())

        # Build lookup for price info from input
        price_map: dict[UUID, int] = {}
        store_map: dict[UUID, UUID | None] = {}
        for inp in input_data.items:
            price_map[inp.shopping_list_item_id] = inp.price_cents
            store_map[inp.shopping_list_item_id] = inp.store_id

        movements: list[MovementOutput] = []
        checked_count = 0

        for item in all_items:
            if not item.checked:
                continue
            checked_count += 1

            # Get item info
            item_name = item.custom_name or ""
            unit = Unit(item.unit) if item.unit else Unit.UN
            price = price_map.get(item.id, 0)
            store_id = store_map.get(item.id, item.store_id)

            # Store snapshot
            store_name: str | None = None
            if store_id:
                store_result = await self.list_repo.session.execute(
                    select(StoreModel).where(StoreModel.id == store_id)
                )
                store_model = store_result.scalar_one_or_none()
                store_name = store_model.name if store_model else None

            # Get sequential code
            seq = await self.movement_repo.get_next_sequential_code(input_data.user_id)

            # Create domain movement
            movement_entity = Movement.create(
                sequential_code=seq,
                quantity=item.estimated_quantity,
                unit=unit,
                price_cents=price,
                store_id=store_id,
                store_name_snapshot=store_name,
                user_id=input_data.user_id,
                pre_registered_item_id=item.pre_registered_item_id,
                shopping_list_item_id=item.id,
                custom_name=item.custom_name,
            )

            # Persist movement
            movement_model = MovementModel(
                id=movement_entity.id,
                sequential_code=movement_entity.sequential_code,
                shopping_list_item_id=movement_entity.shopping_list_item_id,
                pre_registered_item_id=movement_entity.pre_registered_item_id,
                custom_name=movement_entity.custom_name,
                quantity=float(movement_entity.quantity),
                unit=movement_entity.unit.value,
                price_cents=movement_entity.price_cents,
                store_id=movement_entity.store_id,
                store_name_snapshot=movement_entity.store_name_snapshot,
                user_id=movement_entity.user_id,
                purchased_at=movement_entity.purchased_at,
                created_at=movement_entity.created_at,
            )
            self.list_repo.session.add(movement_model)

            # Update stock
            if item.pre_registered_item_id:
                stock_result = await self.list_repo.session.execute(
                    select(StockModel).where(
                        StockModel.pre_registered_item_id == item.pre_registered_item_id,
                        StockModel.user_id == input_data.user_id,
                    )
                )
                stock_model = stock_result.scalar_one_or_none()
                if stock_model:
                    stock_model.current_quantity = float(
                    Decimal(str(stock_model.current_quantity)) + Decimal(str(item.estimated_quantity))
                )
                    if price > 0:
                        stock_model.last_price_cents = price
                    if store_id:
                        stock_model.last_store_id = store_id
                else:
                    # Create stock entry if doesn't exist
                    stock_model = StockModel(
                        pre_registered_item_id=item.pre_registered_item_id,
                        current_quantity=float(item.estimated_quantity),
                        last_price_cents=price if price > 0 else None,
                        last_store_id=store_id,
                        user_id=input_data.user_id,
                    )
                    self.list_repo.session.add(stock_model)

            # Get item name for output
            item_name_out = item.custom_name or ""
            if item.pre_registered_item_id and not item_name_out:
                item_res = await self.list_repo.session.execute(
                    select(ItemModel).where(ItemModel.id == item.pre_registered_item_id)
                )
                item_model = item_res.scalar_one_or_none()
                item_name_out = item_model.name if item_model else ""

            movements.append(
                MovementOutput(
                    id=movement_model.id,
                    sequential_code=seq,
                    item_name=item_name_out,
                    quantity=float(item.estimated_quantity),
                    unit=item.unit,
                    price_cents=price,
                    store_name=store_name,
                )
            )

        # Mark list as completed
        list_model.status = ShoppingListStatus.COMPLETED.value
        list_model.completed_at = datetime.now(timezone.utc)

        await self.uow.commit()

        return CheckoutOutput(
            movements=movements,
            list_status=list_model.status,
        )
