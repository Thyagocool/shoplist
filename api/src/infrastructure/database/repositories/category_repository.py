from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.category_model import CategoryModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[CategoryModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CategoryModel)

    async def find_by_user_id(self, user_id: object) -> list[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.user_id == user_id).order_by(CategoryModel.name)
        )
        return list(result.scalars().all())

    async def count_items(self, category_id: object) -> int:
        from src.infrastructure.database.models.item_model import ItemModel
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.category_id == category_id)
        )
        return len(result.scalars().all())
