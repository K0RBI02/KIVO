"""
KIVO Engine
Rule Engine

EINZIGE RuleEngine im Projekt. Vorher gab es zwei parallele,
widerspruechliche Implementierungen (core/rule_engine.py und
rules/engine.py - letztere war zudem kaputt, da self._rules und
self._triggers nie initialisiert wurden). Das ist jetzt eine
Implementierung, mit Rekursionsschutz (ExecutionContext) und
Mehrfach-Feuer-Schutz (RuleMemory).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from domain.node import Node
from core.events import NodeCreatedEvent
from core.logger import Logger

from .rule_memory import RuleMemory
from .execution_context import ExecutionContext

log = Logger.get("kivo.rules")

Condition = Callable[[Node], bool]
Action = Callable[[Node, Any], None]


@dataclass
class Rule:
    condition: Condition
    action: Action
    name: str = ""


class RuleEngine:

    def __init__(self, domain) -> None:
        self.domain = domain
        self.rules: list[Rule] = []
        self.memory = RuleMemory()
        self.execution_context = ExecutionContext()
        self._attached = False

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def attach(self, event_bus) -> None:
        if self._attached:
            return
        self._attached = True

        def on_node_created(event: NodeCreatedEvent) -> None:
            self.execution_context.enter()
            try:
                for idx, rule in enumerate(self.rules):
                    rule_id = rule.name or f"rule_{idx}"

                    if self.memory.has_fired(rule_id, event.node.id):
                        continue

                    if rule.condition(event.node):
                        log.info("rule fired: %s on %s", rule_id, event.node.name)
                        rule.action(event.node, self.domain)
                        self.memory.mark(rule_id, event.node.id)
            finally:
                self.execution_context.exit()

        event_bus.on(NodeCreatedEvent, on_node_created)

    def evaluate_node(self, node: Node) -> None:
        for idx, rule in enumerate(self.rules):
            rule_id = rule.name or f"rule_{idx}"
            if rule.condition(node):
                self.memory.mark(rule_id, node.id)
                rule.action(node, self.domain)
