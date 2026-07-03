"""
KIVO Engine
Repository Layer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstrakte Schnittstelle fuer Speicherung."""

    @abstractmethod
    def save(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, entity_id: UUID) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> list[T]:
        raise NotImplementedError
