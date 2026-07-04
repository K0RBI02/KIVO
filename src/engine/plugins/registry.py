"""
KIVO Engine
Plugin Registry
"""

from __future__ import annotations

from .plugin import Plugin


class PluginRegistry:

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def exists(self, name: str) -> bool:
        return name in self._plugins

    def all(self) -> tuple[Plugin, ...]:
        return tuple(self._plugins.values())

    def clear(self) -> None:
        self._plugins.clear()
