"""
KIVO Engine
Query Filter
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Filter:
    """Beschreibt eine Bedingung fuer Query-Ergebnisse."""

    field: str
    value: Any
    operator: str = "equals"

    def matches(self, item: Any) -> bool:
        current = getattr(item, self.field, None)

        if self.operator == "equals":
            return current == self.value

        if self.operator == "contains":
            return self.value in current

        if self.operator == "exists":
            return current is not None

        return False
