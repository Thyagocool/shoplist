from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class InventoryDeclaration:
    """A single item declaration during the inventory process.
    
    The user declares how much they currently have at home,
    and the system calculates the need based on max_stock.
    """

    id: UUID = field(default_factory=uuid4)
    shopping_list_id: UUID | None = None
    pre_registered_item_id: UUID | None = None
    declared_quantity: Decimal = Decimal("0")
    calculated_need: Decimal = Decimal("0")
    user_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def declare(
        cls,
        shopping_list_id: UUID,
        pre_registered_item_id: UUID,
        declared_quantity: Decimal,
        max_stock: Decimal,
        user_id: UUID,
    ) -> "InventoryDeclaration":
        """Create a declaration and automatically calculate the need."""
        need = max(max_stock - declared_quantity, Decimal("0"))
        return cls(
            id=uuid4(),
            shopping_list_id=shopping_list_id,
            pre_registered_item_id=pre_registered_item_id,
            declared_quantity=declared_quantity,
            calculated_need=need,
            user_id=user_id,
            created_at=datetime.now(),
        )

    @property
    def needs_purchase(self) -> bool:
        return self.calculated_need > 0
