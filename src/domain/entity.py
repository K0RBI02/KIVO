"""
KIVO Engine
Domain Entity Base
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(slots=True)
class Entity:
    """
    Basisklasse aller KIVO Domain-Objekte.
    Jede Entity besitzt eine eindeutige ID
    und Metadaten ueber Erstellung und Aenderung.
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Aktualisiert den Aenderungszeitpunkt."""
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
