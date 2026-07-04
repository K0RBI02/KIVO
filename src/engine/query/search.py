"""
KIVO Engine
Search System
"""

from __future__ import annotations

from typing import Iterable, Any


class Search:
    """Einfache Textsuche ueber KIVO Objekte."""

    def __init__(self, *, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def find(self, items: Iterable[Any], term: str) -> list[Any]:
        results = []
        for item in items:
            if self._matches(item, term):
                results.append(item)
        return results

    def _matches(self, item: Any, term: str) -> bool:
        if not self.case_sensitive:
            term = term.lower()

        values = []

        if hasattr(item, "name"):
            values.append(item.name)

        if hasattr(item, "properties"):
            values.extend(str(value) for value in item.properties.values())

        if hasattr(item, "tags"):
            values.extend(item.tags)

        for value in values:
            text = str(value)
            if not self.case_sensitive:
                text = text.lower()
            if term in text:
                return True

        return False
