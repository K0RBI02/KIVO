"""
KIVO Engine
Dependency Injection Container
"""

from __future__ import annotations

from typing import Any, Type, TypeVar

from .errors import ServiceNotFoundError

T = TypeVar("T")


class Container:
    """Verwaltet Abhaengigkeiten innerhalb der Engine."""

    def __init__(self) -> None:
        self._services: dict[type[Any], Any] = {}

    def register(self, service_type: Type[T], instance: T) -> None:
        self._services[service_type] = instance

    def resolve(self, service_type: Type[T]) -> T:
        try:
            return self._services[service_type]
        except KeyError as exc:
            raise ServiceNotFoundError(f"Service '{service_type.__name__}' not registered.") from exc

    def has(self, service_type: Type[Any]) -> bool:
        return service_type in self._services

    def remove(self, service_type: Type[Any]) -> None:
        self._services.pop(service_type, None)

    def clear(self) -> None:
        self._services.clear()

    def all(self) -> tuple[Any, ...]:
        return tuple(self._services.values())

    def size(self) -> int:
        return len(self._services)

    def __contains__(self, service_type: Type[Any]) -> bool:
        return service_type in self._services
