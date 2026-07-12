"""Unit tests for domain value objects."""
import pytest

from src.domain.value_objects.email import Email
from src.domain.value_objects.price import Price
from src.domain.value_objects.unit import Unit


class TestEmail:
    def test_valid_email(self):
        email = Email("user@example.com")
        assert str(email) == "user@example.com"

    def test_valid_email_with_plus(self):
        email = Email("user+tag@example.com")
        assert str(email) == "user+tag@example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            Email("invalid")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValueError, match="Invalid email address"):
            Email("user@")

    def test_equality(self):
        e1 = Email("a@b.com")
        e2 = Email("a@b.com")
        assert e1 == e2


class TestPrice:
    def test_from_float(self):
        price = Price.from_float(19.90)
        assert price.cents == 1990

    def test_from_str_br_brazilian(self):
        price = Price.from_str_br("R$ 19,90")
        assert price.cents == 1990

    def test_from_str_br_with_thousands_sep(self):
        """1.234,56 → 123456 cents."""
        price = Price.from_str_br("R$ 1.234,56")
        assert price.cents == 123456

    def test_from_str_br_integer(self):
        price = Price.from_str_br("10")
        assert price.cents == 1000

    def test_to_float(self):
        price = Price(cents=1990)
        assert price.to_float() == 19.90

    def test_to_float_small(self):
        price = Price(cents=50)
        assert price.to_float() == 0.50

    def test_str_format(self):
        price = Price(cents=1990)
        assert str(price) == "R$ 19,90"

    def test_str_format_small(self):
        price = Price(cents=50)
        assert str(price) == "R$ 0,50"


class TestUnit:
    def test_valid_units(self):
        assert Unit.KG.value == "kg"
        assert Unit.G.value == "g"
        assert Unit.L.value == "l"
        assert Unit.UN.value == "un"

    def test_from_string(self):
        assert Unit("kg") == Unit.KG
        assert Unit("un") == Unit.UN

    def test_invalid_unit(self):
        with pytest.raises(ValueError):
            Unit("invalid_unit")
