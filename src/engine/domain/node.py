"""
KIVO Engine
Domain Node
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .entity import Entity
from .property import Property
from .types import NodeType
from .tag import Tag


@dataclass(slots=True)
class Node(Entity):
    """Grundbaustein des KIVO Wissensmodells."""

    name: str = ""
    type: NodeType = NodeType.DEFAULT
    properties: dict[str, Property] = field(default_factory=dict)
    tags: set[Tag] = field(default_factory=set)

    def add_property(self, property: Property) -> None:
        self.properties[property.key] = property
        self.touch()

    def get_property(self, key: str) -> Property | None:
        return self.properties.get(key)

    def remove_property(self, key: str) -> None:
        self.properties.pop(key, None)
        self.touch()

    def add_tag(self, tag: Tag) -> None:
        self.tags.add(tag)
        self.touch()

    def remove_tag(self, tag: Tag) -> None:
        self.tags.discard(tag)
        self.touch()

    def has_tag(self, tag: Tag) -> bool:
        return tag in self.tags

    def has_property(self, key: str) -> bool:
        return key in self.properties

    def all_properties(self) -> tuple[Property, ...]:
        return tuple(self.properties.values())

    def clone(self) -> Node:
        return Node(
            name=self.name,
            type=self.type,
            properties=self.properties.copy(),
            tags=self.tags.copy(),
        )

    def __repr__(self) -> str:
        return f"Node(id={self.id}, name={self.name})"
