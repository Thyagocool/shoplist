"""Unit tests for domain entities."""
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.user import User
from src.domain.entities.category import Category
from src.domain.entities.pre_registered_item import PreRegisteredItem
from src.domain.entities.shopping_list import ShoppingList, ShoppingListStatus
from src.domain.entities.shopping_list_item import ShoppingListItem
from src.domain.entities.inventory import InventoryDeclaration
from src.domain.value_objects.unit import Unit


class TestUser:
    def test_create_user(self):
        user = User.create(name="João", email="joao@email.com", password_hash="hash123")
        assert user.name == "João"
        assert str(user.email) == "joao@email.com"
        assert user.password_hash == "hash123"
        assert user.id is not None


class TestCategory:
    def test_create_category(self):
        uid = uuid4()
        cat = Category.create(name="Carnes", user_id=uid)
        assert cat.name == "Carnes"
        assert cat.user_id == uid


class TestPreRegisteredItem:
    def test_create_item(self):
        uid = uuid4()
        cat_id = uuid4()
        item = PreRegisteredItem.create(
            name="Arroz",
            category_id=cat_id,
            user_id=uid,
            default_unit=Unit.KG,
            default_quantity=Decimal("1"),
            min_stock=Decimal("2"),
            max_stock=Decimal("5"),
        )
        assert item.name == "Arroz"
        assert item.default_unit == Unit.KG
        assert item.active is True

    def test_deactivate(self):
        uid = uuid4()
        item = PreRegisteredItem.create(name="Item", category_id=uuid4(), user_id=uid)
        item.deactivate()
        assert item.active is False


class TestShoppingList:
    def test_create_list(self):
        uid = uuid4()
        lst = ShoppingList.create(name="Feira", user_id=uid)
        assert lst.name == "Feira"
        assert lst.status == ShoppingListStatus.IN_PROGRESS

    def test_complete_list(self):
        uid = uuid4()
        lst = ShoppingList.create(name="Lista", user_id=uid)
        lst.complete()
        assert lst.status == ShoppingListStatus.COMPLETED
        assert lst.completed_at is not None

    def test_cancel_list(self):
        uid = uuid4()
        lst = ShoppingList.create(name="Lista", user_id=uid)
        lst.cancel()
        assert lst.status == ShoppingListStatus.CANCELLED


class TestShoppingListItem:
    def test_from_pre_registered(self):
        list_id = uuid4()
        item_id = uuid4()
        item = ShoppingListItem.from_pre_registered(
            shopping_list_id=list_id,
            pre_registered_item_id=item_id,
            estimated_quantity=Decimal("2"),
            unit=Unit.KG,
            user_id=uuid4(),
        )
        assert item.shopping_list_id == list_id
        assert item.pre_registered_item_id == item_id
        assert item.estimated_quantity == Decimal("2")
        assert item.unit == Unit.KG
        assert item.checked is False

    def test_create_custom(self):
        list_id = uuid4()
        item = ShoppingListItem.create_custom(
            shopping_list_id=list_id,
            name="Leite",
            quantity=Decimal("3"),
            unit=Unit.L,
            user_id=uuid4(),
        )
        assert item.custom_name == "Leite"
        assert item.estimated_quantity == Decimal("3")
        assert item.unit == Unit.L

    def test_toggle_check(self):
        list_id = uuid4()
        item = ShoppingListItem.from_pre_registered(
            shopping_list_id=list_id,
            pre_registered_item_id=uuid4(),
            user_id=uuid4(),
        )
        assert item.checked is False
        item.toggle_check()
        assert item.checked is True
        item.toggle_check()
        assert item.checked is False


class TestInventoryDeclaration:
    def test_declare_with_need(self):
        list_id = uuid4()
        item_id = uuid4()
        decl = InventoryDeclaration.declare(
            shopping_list_id=list_id,
            pre_registered_item_id=item_id,
            declared_quantity=Decimal("1"),
            max_stock=Decimal("5"),
            user_id=uuid4(),
        )
        assert decl.declared_quantity == Decimal("1")
        assert decl.calculated_need == Decimal("4")
        assert decl.needs_purchase is True

    def test_declare_no_need(self):
        decl = InventoryDeclaration.declare(
            shopping_list_id=uuid4(),
            pre_registered_item_id=uuid4(),
            declared_quantity=Decimal("5"),
            max_stock=Decimal("5"),
            user_id=uuid4(),
        )
        assert decl.calculated_need == Decimal("0")
        assert decl.needs_purchase is False

    def test_declare_over_max(self):
        decl = InventoryDeclaration.declare(
            shopping_list_id=uuid4(),
            pre_registered_item_id=uuid4(),
            declared_quantity=Decimal("10"),
            max_stock=Decimal("5"),
            user_id=uuid4(),
        )
        assert decl.calculated_need == Decimal("0")
