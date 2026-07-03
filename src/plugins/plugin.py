"""
KIVO Engine
Plugin System
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class Plugin(ABC):
    """Basisklasse aller KIVO Plugins. Erweitert die Engine ohne den Kern zu aendern."""

    name: str = "unknown"
    version: str = "1.0.0"

    @abstractmethod
    def initialize(self, context: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError
