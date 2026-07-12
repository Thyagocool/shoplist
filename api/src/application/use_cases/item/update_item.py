from uuid import UUID

from sqlalchemy import select

from src.application.dtos.item_dtos import UpdateItemInput, ItemOutput
from src.domain.value_objects.unit import Unit
from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class UpdateItemUseCase:
    def __init__(self, repo: ItemRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, item_id: UUID, user_id: UUID, input_data: UpdateItemInput) -> ItemOutput | None:
        model = await self.repo.find_by_id(item_id)
        if not model or str(model.user_id) != str(user_id):
            return None

        if input_data.name is not None:
            model.name = input_data.name
        if input_data.category_id is not None:
            model.category_id = input_data.category_id
        if input_data.default_unit is not None:
            model.default_unit = Unit(input_data.default_unit).value
        if input_data.default_quantity is not None:
            model.default_quantity = float(input_data.default_quantity)
        if input_data.min_stock is not None:
            model.min_stock = float(input_data.min_stock)
        if input_data.max_stock is not None:
            model.max_stock = float(input_data.max_stock)

        await self.repo.save(model)
        await self.uow.commit()

        # Query category separately to avoid lazy-load issues
        result = await self.repo.session.execute(
            select(CategoryModel).where(CategoryModel.id == model.category_id)
        )
        category = result.scalar_one_or_none()

        return ItemOutput(
            id=model.id,
            name=model.name,
            category_id=model.category_id,
            category_name=category.name if category else "",
            default_unit=model.default_unit,
            default_quantity=model.default_quantity,
            min_stock=model.min_stock,
            max_stock=model.max_stock,
            active=model.active,
        )
