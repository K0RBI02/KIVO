"""
KIVO Search Engine
Result Builder

Aufgabe: aus den Scores fertige SearchResults bauen, sortiert.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..entry import Entry


@dataclass(slots=True, frozen=True)
class SearchResult:
    entry: Entry
    score: float


class ResultBuilder:

    def execute(self, context) -> None:
        results = [
            SearchResult(entry=candidate["entry"], score=context.scores.get(entry_id, 0.0))
            for entry_id, candidate in context.candidates.items()
        ]
        results.sort(key=lambda r: r.score, reverse=True)
        context.results = [r for r in results if r.score > 0]
