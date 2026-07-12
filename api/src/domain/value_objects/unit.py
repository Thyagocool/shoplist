from enum import Enum


class Unit(str, Enum):
    """Standardized units of measurement.
    
    Using an enum prevents free-text unit entries that would break
    stock calculations and reporting.
    """

    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    UN = "un"
    PCT = "pct"
    CX = "cx"
    DZ = "dz"

    def __str__(self) -> str:
        return self.value
