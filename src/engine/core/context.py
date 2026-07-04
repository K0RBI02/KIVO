"""
KIVO Engine
Engine Context

Traegt GENAU EINE Instanz von jedem zentralen Service.
Das ist die einzige Stelle, an der diese Services erzeugt werden.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.manager import DomainManager
from query.engine import QueryEngine
from rules.engine import RuleEngine

from .config import EngineConfig
from .container import Container
from .event_bus import EventBus
from .lifecycle import Lifecycle
from .registry import Registry


@dataclass(slots=True)
class EngineContext:

    config: EngineConfig

    registry: Registry
    container: Container
    event_bus: EventBus
    lifecycle: Lifecycle

    domain: DomainManager
    query: QueryEngine
    rule_engine: RuleEngine

    @classmethod
    def create(cls, config: EngineConfig | None = None) -> EngineContext:

        config = config or EngineConfig()

        registry = Registry()
        container = Container()
        event_bus = EventBus()
        lifecycle = Lifecycle()

        domain = DomainManager(event_bus)
        query = QueryEngine(domain)
        rule_engine = RuleEngine(domain)

        rule_engine.attach(event_bus)

        context = cls(
            config=config,
            registry=registry,
            container=container,
            event_bus=event_bus,
            lifecycle=lifecycle,
            domain=domain,
            query=query,
            rule_engine=rule_engine,
        )

        return context
