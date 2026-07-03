"""
KIVO Engine
Query Index
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from uuid import UUID


class Index:
    """Suchindex fuer schnelle Zugriffe (Begriff -> Entity-IDs)."""

    def __init__(self) -> None:
        self._index: dict[str, set[UUID]] = defaultdict(set)

    def add(self, key: str, entity_id: UUID) -> None:
        self._index[key].add(entity_id)

    def remove(self, key: str, entity_id: UUID) -> None:
        if key in self._index:
            self._index[key].discard(entity_id)

    def search(self, key: str) -> set[UUID]:
        return self._index.get(key, set())

    def build(self, items: list[Any]) -> None:
        for item in items:
            if not hasattr(item, "id"):
                continue

            entity_id = item.id

            if hasattr(item, "name"):
                self.add(item.name.lower(), entity_id)

            if hasattr(item, "tags"):
                for tag in item.tags:
                    self.add(str(tag).lower(), entity_id)

    def clear(self) -> None:
        self._index.clear()
