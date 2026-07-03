"""
KIVO Engine
Transaction System
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import EngineContext

from .command import Command
from .result import CommandResult


@dataclass(slots=True)
class Transaction:
    """Gruppiert mehrere Commands zu einer Einheit (ausfuehren oder zurueckrollen)."""

    id: UUID = field(default_factory=uuid4)
    commands: list[Command] = field(default_factory=list)
    committed: bool = False

    def add(self, command: Command) -> None:
        if self.committed:
            raise RuntimeError("Cannot modify committed transaction.")
        self.commands.append(command)

    def commit(self, context: EngineContext) -> CommandResult:
        if self.committed:
            return CommandResult()

        executed: list[Command] = []

        for command in self.commands:
            if not command.can_execute(context):
                self.rollback(context, executed)
                return CommandResult(success=False, message="Transaction aborted.")

            result = command.execute(context)

            if not result.success:
                self.rollback(context, executed)
                return result

            executed.append(command)

        self.committed = True
        return CommandResult()

    def rollback(self, context: EngineContext, commands: list[Command] | None = None) -> None:
        if commands is None:
            commands = self.commands
        for command in reversed(commands):
            command.undo(context)
        self.committed = False

    def clear(self) -> None:
        self.commands.clear()
        self.committed = False

    def size(self) -> int:
        return len(self.commands)
