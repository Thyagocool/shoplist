from uuid import UUID

from src.application.dtos.shopping_list_dtos import ShoppingListOutput
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
                completed_at=m.completed_at,
            )
            for m in models
        ]
