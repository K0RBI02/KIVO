"""
KIVO Search Engine
Pipeline Context

Das Datenobjekt, das durch alle Pipeline-Module wandert.
Jedes Modul liest was es braucht und schreibt sein Ergebnis dazu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class PipelineContext:
    raw_query: str

    tokens: list[str] = field(default_factory=list)
    filtered_tokens: list[str] = field(default_factory=list)
    normalized_tokens: list[str] = field(default_factory=list)

    # Gewichtete Query-Keywords (nach Discovery-Wissen der Engine)
    weighted_tokens: dict[str, float] = field(default_factory=dict)

    # Kandidaten vor dem Scoring: entry_id -> roh-Infos fuer den Scorer
    candidates: dict[UUID, dict] = field(default_factory=dict)

    # entry_id -> Score
    scores: dict[UUID, float] = field(default_factory=dict)

    results: list = field(default_factory=list)
