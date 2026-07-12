from uuid import UUID

from src.application.dtos.store_dtos import UpdateStoreInput, StoreOutput
from src.infrastructure.database.repositories.store_repository import StoreRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class UpdateStoreUseCase:
    def __init__(self, repo: StoreRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(
        self, store_id: UUID, user_id: UUID, input_data: UpdateStoreInput
    ) -> StoreOutput | None:
        model = await self.repo.find_by_id(store_id)
        if not model or str(model.user_id) != str(user_id):
            return None

        if input_data.name is not None:
            model.name = input_data.name

        await self.repo.save(model)
        await self.uow.commit()

        return StoreOutput(id=model.id, name=model.name)
