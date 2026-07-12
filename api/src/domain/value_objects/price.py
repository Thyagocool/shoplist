from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Value object representing a monetary price in cents.
    
    Stores prices as integers (cents) to avoid floating-point issues.
    """

    cents: int

    def __post_init__(self) -> None:
        if self.cents < 0:
            raise ValueError(f"Price cannot be negative: {self.cents}")

    @classmethod
    def from_float(cls, value: float) -> "Price":
        """Create Price from a float value (e.g., 12.90)."""
        return cls(cents=int(round(value * 100)))

    @classmethod
    def from_str_br(cls, value: str) -> "Price":
        """Parse Brazilian price format: 'R$ 12,90', '12,90', or '12.90'."""
        cleaned = (
            value.replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        return cls.from_float(float(cleaned))

    def to_float(self) -> float:
        """Convert back to float (e.g., 12.90)."""
        return round(self.cents / 100, 2)

    def __str__(self) -> str:
        real = self.cents // 100
        centavos = self.cents % 100
        return f"R$ {real},{centavos:02d}"
