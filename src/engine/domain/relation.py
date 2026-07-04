"""
KIVO Engine
Domain Relation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from .entity import Entity
from .property import Property
from .types import RelationType


@dataclass(slots=True)
class Relation(Entity):
    """Verbindung zwischen zwei KIVO Nodes."""

    source_id: UUID | None = None
    target_id: UUID | None = None
    type: RelationType = RelationType.DEFAULT
    weight: float = 1.0
    directed: bool = True
    properties: dict[str, Property] = field(default_factory=dict)

    def connects(self, node_id: UUID) -> bool:
        return self.source_id == node_id or self.target_id == node_id

    def contains(self, source_id: UUID, target_id: UUID) -> bool:
        return self.source_id == source_id and self.target_id == target_id

    def add_property(self, property: Property) -> None:
        self.properties[property.key] = property
        self.touch()

    def get_property(self, key: str) -> Property | None:
        return self.properties.get(key)

    def remove_property(self, key: str) -> None:
        self.properties.pop(key, None)
        self.touch()

    def has_property(self, key: str) -> bool:
        return key in self.properties

    def all_properties(self) -> tuple[Property, ...]:
        return tuple(self.properties.values())

    def clone(self) -> Relation:
        return Relation(
            source_id=self.source_id,
            target_id=self.target_id,
            type=self.type,
            weight=self.weight,
            directed=self.directed,
            properties={k: v.clone() for k, v in self.properties.items()},
        )

    def __repr__(self) -> str:
        return f"Relation({self.source_id} -> {self.target_id}, type={self.type})"
