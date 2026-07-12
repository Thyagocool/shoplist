from uuid import UUID

from src.application.dtos.store_dtos import CreateStoreInput, StoreOutput
from src.domain.entities.store import Store
from src.infrastructure.database.models.store_model import StoreModel
from src.infrastructure.database.repositories.store_repository import StoreRepository
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class CreateStoreUseCase:
    def __init__(self, repo: StoreRepository, uow: SQLAlchemyUnitOfWork) -> None:
        self.repo = repo
        self.uow = uow

    async def execute(self, input_data: CreateStoreInput) -> StoreOutput:
        store = Store.create(name=input_data.name, user_id=input_data.user_id)

        model = StoreModel(id=store.id, name=store.name, user_id=store.user_id)
        await self.repo.save(model)
        await self.uow.commit()

        return StoreOutput(id=model.id, name=model.name)
