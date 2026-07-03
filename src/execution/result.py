"""
KIVO Engine
Execution Result
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandResult:
    success: bool = True
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return not self.success

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.success = False

    def set_data(self, key: str, value: Any) -> None:
        self.data[key] = value
