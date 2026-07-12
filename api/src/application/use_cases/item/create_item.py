from uuid import UUID

from src.application.dtos.item_dtos import CreateItemInput, ItemOutput
from src.domain.entities.pre_registered_item import PreRegisteredItem
from src.domain.value_objects.unit import Unit
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.models.stock_model import StockModel
from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateItemUseCase:
    def __init__(self, repo: ItemRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, input_data: CreateItemInput) -> ItemOutput:
        unit = Unit(input_data.default_unit) if input_data.default_unit else Unit.UN

        item = PreRegisteredItem.create(
            name=input_data.name,
            category_id=input_data.category_id,
            user_id=input_data.user_id,
            default_unit=unit,
            default_quantity=input_data.default_quantity,
            min_stock=input_data.min_stock,
            max_stock=input_data.max_stock,
        )

        # Persist item
        model = ItemModel(
            id=item.id,
            name=item.name,
            category_id=item.category_id,
            default_unit=item.default_unit.value,
            default_quantity=float(item.default_quantity),
            min_stock=float(item.min_stock),
            max_stock=float(item.max_stock),
            user_id=item.user_id,
            active=item.active,
        )
        await self.repo.save(model)

        # Create stock entry for the item
        stock = StockModel(
            pre_registered_item_id=item.id,
            current_quantity=0.0,
            user_id=input_data.user_id,
        )
        self.repo.session.add(stock)

        await self.uow.commit()

        from src.infrastructure.database.models.category_model import CategoryModel
        from sqlalchemy import select

        result = await self.repo.session.execute(
            select(CategoryModel).where(CategoryModel.id == input_data.category_id)
        )
        category = result.scalar_one_or_none()

        return ItemOutput(
            id=item.id,
            name=item.name,
            category_id=item.category_id,
            category_name=category.name if category else "",
            default_unit=item.default_unit.value,
            default_quantity=item.default_quantity,
            min_stock=item.min_stock,
            max_stock=item.max_stock,
            active=item.active,
        )
