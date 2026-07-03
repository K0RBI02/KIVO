"""
KIVO Engine
Seed Layer (deterministisch + idempotent)
"""

from __future__ import annotations

from domain.node import Node


class Seed:

    def __init__(self, domain) -> None:
        self.domain = domain

    def node(self, name: str) -> Node:
        """Erstellt Node nur wenn Name noch nicht existiert."""

        existing = self.domain.get_by_name(name)

        if existing:
            return existing

        node = Node(name=name)
        self.domain.add_node(node)

        return node
