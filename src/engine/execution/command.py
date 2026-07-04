"""
KIVO Engine
Command System
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import EngineContext

from .result import CommandResult


class Command(ABC):
    """Basisklasse aller Engine-Aktionen. Jede Aenderung laeuft ueber ein Command."""

    name: str = "Command"
    description: str = ""

    def __init__(self) -> None:
        self.id: UUID = uuid4()
        self.created_at: datetime = datetime.now(timezone.utc)

    @abstractmethod
    def execute(self, context: EngineContext) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def undo(self, context: EngineContext) -> None:
        raise NotImplementedError

    def can_execute(self, context: EngineContext) -> bool:
        return True
