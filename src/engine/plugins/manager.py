"""
KIVO Engine
Plugin Manager
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import EngineContext

from .loader import PluginLoader
from .registry import PluginRegistry


class PluginManager:
    """Steuert den kompletten Plugin-Lebenszyklus."""

    def __init__(self, context: EngineContext) -> None:
        self.context = context
        self.loader = PluginLoader()
        self.registry = PluginRegistry()

    def load_plugin(self, module_name: str) -> None:
        plugin = self.loader.load(module_name)
        plugin.initialize(self.context)
        self.registry.register(plugin)

    def load_directory(self, directory: Path) -> None:
        for module in self.loader.discover(directory):
            self.load_plugin(module)

    def shutdown(self) -> None:
        for plugin in self.registry.all():
            plugin.shutdown()
        self.registry.clear()
