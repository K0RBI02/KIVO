"""
KIVO Engine
Domain Manager

EINZIGE Quelle der Wahrheit fuer Nodes/Relations.
Wichtig: es darf im ganzen Projekt immer nur EINE
DomainManager-Instanz pro Engine geben (siehe core/context.py).
"""

from __future__ import annotations

from uuid import UUID

from .node import Node
from .relation import Relation
from core.errors import DomainError, EntityNotFoundError, DuplicateEntityError
from core.events import NodeCreatedEvent, RelationCreatedEvent


class DomainManager:

    def __init__(self, event_bus) -> None:
        self._event_bus = event_bus
        self._nodes: dict[UUID, Node] = {}
        self._relations: dict[UUID, Relation] = {}

    def add_node(self, node: Node) -> None:
        if node.id in self._nodes:
            raise DuplicateEntityError(f"Node '{node.id}' already exists.")

        self._nodes[node.id] = node
        self._event_bus.emit(NodeCreatedEvent(node))

    def get_node(self, node_id: UUID) -> Node:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise EntityNotFoundError(f"Node '{node_id}' not found.") from exc

    def get_by_name(self, name: str) -> Node | None:
        for node in self._nodes.values():
            if node.name == name:
                return node
        return None

    def remove_node(self, node_id: UUID) -> None:
        self._nodes.pop(node_id, None)
        self._relations = {
            rid: rel for rid, rel in self._relations.items() if not rel.connects(node_id)
        }

    def add_relation(self, relation: Relation) -> None:
        if relation.source_id not in self._nodes:
            raise DomainError("Source node does not exist.")
        if relation.target_id not in self._nodes:
            raise DomainError("Target node does not exist.")

        self._relations[relation.id] = relation
        self._event_bus.emit(RelationCreatedEvent(relation))

    def get_relation(self, relation_id: UUID) -> Relation:
        try:
            return self._relations[relation_id]
        except KeyError as exc:
            raise DomainError(f"Relation '{relation_id}' not found.") from exc

    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._nodes.values())

    def relations(self) -> tuple[Relation, ...]:
        return tuple(self._relations.values())

    def clear(self) -> None:
        self._nodes.clear()
        self._relations.clear()

    def has_node(self, node_id: UUID) -> bool:
        return node_id in self._nodes

    def has_relation(self, relation_id: UUID) -> bool:
        return relation_id in self._relations

    def get_connected_nodes(self, node_id: UUID) -> tuple[Node, ...]:
        if node_id not in self._nodes:
            raise EntityNotFoundError(f"Node '{node_id}' not found.")

        connected: list[Node] = []

        for relation in self._relations.values():
            if relation.source_id == node_id:
                n = self._nodes.get(relation.target_id)
                if n:
                    connected.append(n)
            elif relation.target_id == node_id:
                n = self._nodes.get(relation.source_id)
                if n:
                    connected.append(n)

        return tuple(connected)
