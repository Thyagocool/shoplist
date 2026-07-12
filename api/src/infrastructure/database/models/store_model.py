from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base, UUIDMixin


class StoreModel(UUIDMixin, Base):
    __tablename__ = "stores"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="stores")
    movements = relationship("MovementModel", back_populates="store", lazy="selectin")
