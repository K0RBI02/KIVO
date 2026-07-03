"""
KIVO Engine
Command Executor
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import EngineContext

from collections import deque

from .command import Command
from .result import CommandResult
from .transaction import Transaction


class Executor:
    """Fuehrt Commands aus und verwaltet die Ausfuehrungshistorie (Undo/Redo)."""

    def __init__(self, context: EngineContext) -> None:
        self._context = context
        self._history: deque[Command] = deque()
        self._redo_stack: deque[Command] = deque()

    def execute(self, command: Command) -> CommandResult:
        if not command.can_execute(self._context):
            return CommandResult(success=False, message="Command cannot be executed.")

        result = command.execute(self._context)

        if result.success:
            self._history.append(command)
            self._redo_stack.clear()

        return result

    def execute_transaction(self, transaction: Transaction) -> CommandResult:
        return transaction.commit(self._context)

    def undo(self) -> CommandResult:
        if not self._history:
            return CommandResult()

        command = self._history.pop()
        command.undo(self._context)
        self._redo_stack.append(command)

        return CommandResult()

    def redo(self) -> CommandResult:
        if not self._redo_stack:
            return CommandResult()

        command = self._redo_stack.pop()
        result = command.execute(self._context)

        if result.success:
            self._history.append(command)

        return result

    def clear_history(self) -> None:
        self._history.clear()
        self._redo_stack.clear()

    def history_size(self) -> int:
        return len(self._history)

    def redo_size(self) -> int:
        return len(self._redo_stack)
