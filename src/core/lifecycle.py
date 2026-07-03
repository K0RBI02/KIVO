"""
KIVO Engine
Lifecycle
"""

from __future__ import annotations

from enum import Enum, auto


class LifecycleState(Enum):
    CREATED = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


class Lifecycle:

    def __init__(self) -> None:
        self._state = LifecycleState.CREATED

    @property
    def state(self) -> LifecycleState:
        return self._state

    def set(self, state: LifecycleState) -> None:
        self._state = state

    def is_running(self) -> bool:
        return self._state is LifecycleState.RUNNING

    def is_initialized(self) -> bool:
        return self._state.value >= LifecycleState.INITIALIZED.value
