from uuid import UUID

from src.infrastructure.database.repositories.list_repository import ShoppingListRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class RemoveListItemUseCase:
    def __init__(self, repo: ShoppingListRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, item_id: UUID, user_id: UUID) -> bool:
        # Verifica se o item existe e pertence ao usuário
        from sqlalchemy import select

        from src.infrastructure.database.models.list_item_model import ShoppingListItemModel
        from src.infrastructure.database.models.list_model import ShoppingListModel

        result = await self.repo.session.execute(
            select(ShoppingListItemModel)
            .join(ShoppingListModel, ShoppingListItemModel.shopping_list_id == ShoppingListModel.id)
            .where(
                ShoppingListItemModel.id == item_id,
                ShoppingListModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        # Verifica se a lista ainda está editável
        list_model = await self.repo.find_by_id(model.shopping_list_id)
        if list_model and list_model.status not in ("pending", "in_progress"):
            raise ValueError("Cannot modify completed/cancelled list")

        await self.repo.session.delete(model)
        await self.repo.session.flush()
        await self.uow.commit()
        return True
