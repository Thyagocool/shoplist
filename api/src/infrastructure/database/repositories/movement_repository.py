from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.database.models.movement_model import MovementModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class MovementRepository(BaseRepository[MovementModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MovementModel)

    async def find_by_user_id(
        self,
        user_id: UUID,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        item_id: UUID | None = None,
        store_id: UUID | None = None,
    ) -> list[MovementModel]:
        query = select(MovementModel).where(MovementModel.user_id == user_id)

        if from_date:
            query = query.where(MovementModel.purchased_at >= from_date)
        if to_date:
            query = query.where(MovementModel.purchased_at <= to_date)
        if item_id:
            query = query.where(MovementModel.pre_registered_item_id == item_id)
        if store_id:
            query = query.where(MovementModel.store_id == store_id)

        query = query.order_by(MovementModel.purchased_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_next_sequential_code(self, user_id: UUID) -> str:
        """Generate the next sequential code like MOV-001, MOV-002..."""
        result = await self.session.execute(
            select(MovementModel)
            .where(MovementModel.user_id == user_id)
            .order_by(MovementModel.created_at.desc())
            .limit(1)
        )
        last = result.scalar_one_or_none()
        if last is None:
            return "MOV-001"
        last_num = int(last.sequential_code.split("-")[1])
        return f"MOV-{last_num + 1:03d}"
