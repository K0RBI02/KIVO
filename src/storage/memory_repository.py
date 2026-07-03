"""
KIVO Engine
In-Memory Repository Implementation
"""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from .repository import Repository

T = TypeVar("T")


class MemoryRepository(Repository[T]):

    def __init__(self) -> None:
        self._data: dict[UUID, T] = {}

    def save(self, entity: T) -> None:
        self._data[entity.id] = entity

    def get(self, entity_id: UUID) -> T | None:
        return self._data.get(entity_id)

    def delete(self, entity_id: UUID) -> None:
        self._data.pop(entity_id, None)

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._data

    def all(self) -> list[T]:
        return list(self._data.values())
