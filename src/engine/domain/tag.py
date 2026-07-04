"""
KIVO Engine
Domain Tag
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Tag:
    """Unveraenderliches Tag eines KIVO-Objekts."""

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip().lower())

    def __str__(self) -> str:
        return self.name
