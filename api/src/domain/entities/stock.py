from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Stock:
    """Current stock level and last purchase info for an item."""

    id: UUID = field(default_factory=uuid4)
    pre_registered_item_id: UUID | None = None
    current_quantity: Decimal = Decimal("0")
    last_price_cents: int | None = None
    last_store_id: UUID | None = None
    user_id: UUID | None = None
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, pre_registered_item_id: UUID, user_id: UUID) -> "Stock":
        return cls(
            id=uuid4(),
            pre_registered_item_id=pre_registered_item_id,
            current_quantity=Decimal("0"),
            user_id=user_id,
            updated_at=datetime.now(),
        )

    def add_purchase(
        self,
        quantity: Decimal,
        price_cents: int | None,
        store_id: UUID | None,
    ) -> None:
        """Update stock after a purchase."""
        self.current_quantity += quantity
        if price_cents is not None:
            self.last_price_cents = price_cents
        if store_id is not None:
            self.last_store_id = store_id
        self.updated_at = datetime.now()

    def is_below_minimum(self, min_stock: Decimal) -> bool:
        """Check if stock is below the desired minimum."""
        return self.current_quantity < min_stock
