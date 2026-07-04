"""
KIVO Engine
Main Engine Controller
"""

from __future__ import annotations

import logging

from domain.manager import DomainManager

from .config import EngineConfig
from .context import EngineContext
from .lifecycle import LifecycleState
from .logger import Logger


class Engine:
    """Hauptklasse der KIVO Engine."""

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.context = EngineContext.create(config)
        self.logger = Logger.get("kivo.engine")

    @property
    def state(self) -> LifecycleState:
        return self.context.lifecycle.state

    def initialize(self) -> None:
        self.context.lifecycle.set(LifecycleState.INITIALIZING)

        Logger.configure(
            level=self._log_level(),
            log_file=self.context.config.log_file,
        )

        self._register_core_services()

        self.context.lifecycle.set(LifecycleState.INITIALIZED)
        self.context.event_bus.emit("engine.initialized")

    def start(self) -> None:
        self.context.lifecycle.set(LifecycleState.STARTING)
        self.context.lifecycle.set(LifecycleState.RUNNING)
        self.context.event_bus.emit("engine.started")
        self.logger.info("KIVO Engine started.")

    def stop(self) -> None:
        self.context.lifecycle.set(LifecycleState.STOPPING)
        self.context.event_bus.emit("engine.stopping")
        self.context.lifecycle.set(LifecycleState.STOPPED)
        self.logger.info("KIVO Engine stopped.")

    def is_initialized(self) -> bool:
        return self.state is LifecycleState.INITIALIZED

    def is_running(self) -> bool:
        return self.state is LifecycleState.RUNNING

    def _register_core_services(self) -> None:
        """
        Registriert interne Engine-Services im Container.

        WICHTIG (das war der Hauptbug im alten Code): hier wird KEIN
        neuer DomainManager mehr erzeugt. Es gibt nur die eine Instanz
        aus self.context.domain - die wird registriert, damit Container-
        Consumer immer denselben Zustand sehen wie context.domain.
        """

        self.context.container.register(EngineContext, self.context)
        self.context.container.register(DomainManager, self.context.domain)

    def _log_level(self) -> int:
        level = self.context.config.log_level.upper()
        return getattr(logging, level, logging.INFO)
