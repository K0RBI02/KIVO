"""
KIVO Engine
Domain Events
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.node import Node
from domain.relation import Relation


@dataclass(frozen=True)
class NodeCreatedEvent:
    node: Node


@dataclass(frozen=True)
class RelationCreatedEvent:
    relation: Relation
