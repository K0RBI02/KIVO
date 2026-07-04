"""
KIVO Engine
Plugin Loader
"""

from __future__ import annotations

import importlib
from pathlib import Path

from .plugin import Plugin


class PluginLoader:

    def load(self, module_name: str) -> Plugin:
        module = importlib.import_module(module_name)
        return getattr(module, "plugin")

    def discover(self, directory: Path) -> list[str]:
        modules: list[str] = []
        for file in directory.glob("*.py"):
            if file.name.startswith("_"):
                continue
            modules.append(file.stem)
        return modules
