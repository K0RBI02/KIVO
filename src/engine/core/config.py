"""
KIVO Engine
Configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class EngineConfig:
    project_dir: Path | None = None
    log_level: str = "INFO"
    log_file: Path | None = None
    auto_save: bool = True
    plugin_directory: Path | None = None
    cache_enabled: bool = True
    debug: bool = False
    custom: dict[str, object] = field(default_factory=dict)
