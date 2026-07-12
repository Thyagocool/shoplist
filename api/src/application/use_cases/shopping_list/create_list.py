from uuid import UUID

from src.application.dtos.shopping_list_dtos import CreateShoppingListInput, ShoppingListOutput
from src.domain.entities.shopping_list import ShoppingList
from src.infrastructure.database.models.list_model import ShoppingListModel
from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateShoppingListUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, input_data: CreateShoppingListInput) -> ShoppingListOutput:
        entity = ShoppingList.create(
            name=input_data.name,
            store_id=input_data.store_id,
            user_id=input_data.user_id,
        )

        model = ShoppingListModel(
            id=entity.id,
            name=entity.name,
            status=entity.status.value,
            user_id=entity.user_id,
        )
        await self.repo.save(model)
        await self.uow.commit()

        return ShoppingListOutput(
            id=model.id,
            name=model.name,
            status=model.status,
        )
