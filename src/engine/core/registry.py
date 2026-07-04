"""
KIVO Engine
Service Registry

Registriert Services, Parser, Plugins, Commands usw. per Name
(im Unterschied zum Container, der per Typ aufloest).
"""

from __future__ import annotations

from typing import Any

from .errors import DuplicateRegistrationError, ServiceNotFoundError


class Registry:

    def __init__(self) -> None:
        self._items: dict[str, Any] = {}

    def register(self, name: str, instance: Any, *, overwrite: bool = False) -> None:
        if name in self._items and not overwrite:
            raise DuplicateRegistrationError(f"'{name}' is already registered.")
        self._items[name] = instance

    def unregister(self, name: str) -> None:
        self._items.pop(name, None)

    def get(self, name: str) -> Any:
        try:
            return self._items[name]
        except KeyError as exc:
            raise ServiceNotFoundError(f"'{name}' not found.") from exc

    def get_or_default(self, name: str, default: Any = None) -> Any:
        return self._items.get(name, default)

    def has(self, name: str) -> bool:
        return name in self._items

    def clear(self) -> None:
        self._items.clear()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._items.keys()))

    def values(self) -> tuple[Any, ...]:
        return tuple(self._items.values())

    def items(self) -> tuple[tuple[str, Any], ...]:
        return tuple(self._items.items())

    def size(self) -> int:
        return len(self._items)

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items.items())
