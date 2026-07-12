import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Value object representing an email address."""

    value: str

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    @staticmethod
    def _is_valid(value: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    def __str__(self) -> str:
        return self.value
