"""
KIVO Engine
Event Bus
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Any

from .logger import Logger

log = Logger.get("kivo.events")


class EventBus:
    """
    Zentraler Event-Bus.

    Ein Event-Typ kann beliebig viele Handler haben.
    Handler-Reihenfolge = Registrierungsreihenfolge.
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def on(self, event_type: type, handler: Callable[[Any], None]) -> None:
        self._handlers[event_type].append(handler)

    def emit(self, event: Any) -> None:
        log.debug("event emitted: %s", type(event).__name__)

        for handler in list(self._handlers.get(type(event), [])):
            handler(event)
