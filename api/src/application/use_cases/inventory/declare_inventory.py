from uuid import UUID

from sqlalchemy import select

from src.application.dtos.inventory_dtos import DeclareInventoryInput, InventoryOutput
from src.domain.entities.inventory import InventoryDeclaration
from src.infrastructure.database.models.inventory_model import InventoryModel
from src.infrastructure.database.models.item_model import ItemModel
from src.infrastructure.database.repositories.inventory_repository import InventoryRepository
from src.infrastructure.database.repositories.item_repository import ItemRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class DeclareInventoryUseCase:
    def __init__(
        self,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
        uow: SQLAlchemyUnitOfWork,
    ) -> None:
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo
        self.uow = uow

    async def execute(self, input_data: DeclareInventoryInput) -> InventoryOutput:
        # Get item to find max_stock
        item_model = await self.item_repo.find_by_id(input_data.pre_registered_item_id)
        if not item_model or str(item_model.user_id) != str(input_data.user_id):
            raise ValueError("Item not found")

        max_stock = item_model.max_stock

        entity = InventoryDeclaration.declare(
            shopping_list_id=input_data.shopping_list_id,
            pre_registered_item_id=input_data.pre_registered_item_id,
            declared_quantity=input_data.declared_quantity,
            max_stock=max_stock,
            user_id=input_data.user_id,
        )

        from datetime import datetime, timezone

        model = InventoryModel(
            id=entity.id,
            shopping_list_id=entity.shopping_list_id,
            pre_registered_item_id=entity.pre_registered_item_id,
            declared_quantity=float(entity.declared_quantity),
            calculated_need=float(entity.calculated_need),
            user_id=entity.user_id,
            created_at=datetime.now(timezone.utc),
        )
        await self.inventory_repo.save(model)
        await self.uow.commit()

        return InventoryOutput(
            id=model.id,
            shopping_list_id=model.shopping_list_id,
            pre_registered_item_id=model.pre_registered_item_id,
            declared_quantity=model.declared_quantity,
            calculated_need=model.calculated_need,
            item_name=item_model.name,
        )
