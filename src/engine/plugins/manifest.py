"""
KIVO Engine
Plugin Manifest
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PluginManifest:
    name: str
    version: str
    author: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    enabled: bool = True
