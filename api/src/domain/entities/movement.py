from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.value_objects.unit import Unit


@dataclass
class Movement:
    """A purchase movement — represents a real purchase of an item.
    
    This is the core financial/stock record. Each movement is immutable
    once created (like a ledger entry).
    """

    id: UUID = field(default_factory=uuid4)
    sequential_code: str = ""
    shopping_list_item_id: UUID | None = None
    pre_registered_item_id: UUID | None = None
    custom_name: str | None = None
    quantity: Decimal = Decimal("0")
    unit: Unit = Unit.UN
    price_cents: int = 0
    store_id: UUID | None = None
    store_name_snapshot: str | None = None
    photo_url: str | None = None
    notes: str | None = None
    user_id: UUID | None = None
    purchased_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        sequential_code: str,
        quantity: Decimal,
        unit: Unit,
        price_cents: int,
        store_id: UUID | None,
        store_name_snapshot: str | None,
        user_id: UUID,
        pre_registered_item_id: UUID | None = None,
        shopping_list_item_id: UUID | None = None,
        custom_name: str | None = None,
        photo_url: str | None = None,
        notes: str | None = None,
    ) -> "Movement":
        return cls(
            id=uuid4(),
            sequential_code=sequential_code,
            shopping_list_item_id=shopping_list_item_id,
            pre_registered_item_id=pre_registered_item_id,
            custom_name=custom_name,
            quantity=quantity,
            unit=unit,
            price_cents=price_cents,
            store_id=store_id,
            store_name_snapshot=store_name_snapshot,
            photo_url=photo_url,
            notes=notes,
            user_id=user_id,
            purchased_at=datetime.now(),
            created_at=datetime.now(),
        )
