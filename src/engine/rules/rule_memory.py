"""
KIVO Engine
Rule Memory

Verhindert, dass dieselbe Regel auf demselben Node
mehrfach feuert.
"""

from __future__ import annotations


class RuleMemory:

    def __init__(self) -> None:
        self._fired: set[tuple[str, str]] = set()

    def has_fired(self, rule_id: str, node_id) -> bool:
        return (rule_id, str(node_id)) in self._fired

    def mark(self, rule_id: str, node_id) -> None:
        self._fired.add((rule_id, str(node_id)))

    def clear(self) -> None:
        self._fired.clear()
