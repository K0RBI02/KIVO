"""
KIVO Engine
Serialization System
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from typing import Any


class Serializer(ABC):

    @abstractmethod
    def serialize(self, obj: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: str) -> Any:
        raise NotImplementedError


class JsonSerializer(Serializer):

    def serialize(self, obj: Any) -> str:
        data = asdict(obj) if is_dataclass(obj) else obj
        return json.dumps(data, indent=4, default=str)

    def deserialize(self, data: str) -> Any:
        return json.loads(data)
