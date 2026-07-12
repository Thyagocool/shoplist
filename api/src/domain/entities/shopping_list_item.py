from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.value_objects.unit import Unit


@dataclass
class ShoppingListItem:
    """An item within a shopping list."""

    id: UUID = field(default_factory=uuid4)
    shopping_list_id: UUID | None = None
    pre_registered_item_id: UUID | None = None
    custom_name: str | None = None
    estimated_quantity: Decimal = Decimal("1")
    unit: Unit = Unit.UN
    checked: bool = False
    price_cents: int | None = None
    store_id: UUID | None = None
    photo_url: str | None = None
    user_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_pre_registered(
        cls,
        shopping_list_id: UUID,
        pre_registered_item_id: UUID,
        estimated_quantity: Decimal = Decimal("1"),
        unit: Unit = Unit.UN,
        user_id: UUID | None = None,
    ) -> "ShoppingListItem":
        """Create a list item from a pre-registered catalog item."""
        return cls(
            id=uuid4(),
            shopping_list_id=shopping_list_id,
            pre_registered_item_id=pre_registered_item_id,
            estimated_quantity=estimated_quantity,
            unit=unit,
            user_id=user_id,
            created_at=datetime.now(),
        )

    @classmethod
    def create_custom(
        cls,
        shopping_list_id: UUID,
        name: str,
        quantity: Decimal,
        unit: Unit,
        user_id: UUID,
    ) -> "ShoppingListItem":
        """Create a custom (ad-hoc) list item not in catalog."""
        return cls(
            id=uuid4(),
            shopping_list_id=shopping_list_id,
            custom_name=name,
            estimated_quantity=quantity,
            unit=unit,
            user_id=user_id,
            created_at=datetime.now(),
        )

    def toggle_check(self) -> None:
        self.checked = not self.checked

    @property
    def display_name(self) -> str:
        if self.custom_name:
            return self.custom_name
        return ""  # Will be resolved from pre_registered_item at query time
