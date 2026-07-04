"""
KIVO Engine
Domain Property
"""

from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any

from .types import PropertyType


@dataclass(slots=True)
class Property:
    """Typisierte Eigenschaft eines KIVO-Objektes."""

    key: str
    type: PropertyType
    value: Any = None
    required: bool = False
    readonly: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, value: Any) -> bool:
        if value is None:
            return not self.required

        match self.type:
            case PropertyType.STRING:
                return isinstance(value, str)
            case PropertyType.INTEGER:
                return isinstance(value, int)
            case PropertyType.FLOAT:
                return isinstance(value, float)
            case PropertyType.BOOLEAN:
                return isinstance(value, bool)
            case PropertyType.LIST:
                return isinstance(value, list)
            case PropertyType.DICT:
                return isinstance(value, dict)
            case _:
                return True

    def set_value(self, value: Any) -> None:
        if self.readonly:
            raise ValueError(f"Property '{self.key}' is readonly.")
        if not self.validate(value):
            raise ValueError(f"Invalid value for Property '{self.key}'.")
        self.value = value

    def clone(self) -> Property:
        return Property(
            key=self.key,
            type=self.type,
            value=deepcopy(self.value),
            required=self.required,
            readonly=self.readonly,
            metadata=deepcopy(self.metadata),
        )
