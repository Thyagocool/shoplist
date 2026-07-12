from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.value_objects.unit import Unit


@dataclass
class PreRegisteredItem:
    """An item in the user's personal catalog.
    
    Each user has their own catalog of items they regularly buy.
    The min_stock and max_stock define the desired inventory range.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    category_id: UUID | None = None
    default_unit: Unit = Unit.UN
    default_quantity: Decimal = Decimal("1")
    min_stock: Decimal = Decimal("0")
    max_stock: Decimal = Decimal("0")
    user_id: UUID | None = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        name: str,
        category_id: UUID,
        user_id: UUID,
        default_unit: Unit = Unit.UN,
        default_quantity: Decimal = Decimal("1"),
        min_stock: Decimal = Decimal("0"),
        max_stock: Decimal = Decimal("0"),
    ) -> "PreRegisteredItem":
        now = datetime.now()
        return cls(
            id=uuid4(),
            name=name,
            category_id=category_id,
            default_unit=default_unit,
            default_quantity=default_quantity,
            min_stock=min_stock,
            max_stock=max_stock,
            user_id=user_id,
            active=True,
            created_at=now,
            updated_at=now,
        )

    def deactivate(self) -> None:
        """Soft delete - item stays in open lists but won't appear in new ones."""
        self.active = False
        self.updated_at = datetime.now()
