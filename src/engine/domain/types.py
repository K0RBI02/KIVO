"""
KIVO Engine
Domain Types
"""

from __future__ import annotations
from enum import Enum


class NodeType(str, Enum):
    DEFAULT = "default"
    ENTITY = "entity"
    CONCEPT = "concept"
    EVENT = "event"
    PERSON = "person"
    PLACE = "place"
    DOCUMENT = "document"


class RelationType(str, Enum):
    DEFAULT = "default"
    PARENT = "parent"
    CHILD = "child"
    LINK = "link"
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    CONTAINS = "contains"


class PropertyType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    OBJECT = "object"
