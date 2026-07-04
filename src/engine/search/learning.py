"""
KIVO Search Engine
Learning (Benutzerverhalten)

Laut Spec: "Benutzerverhalten darf niemals einen besseren Treffer
ueberholen." Deshalb ist der Bonus hier hart gedeckelt und liegt
WEIT unter Titel/Inhalt/Fuzzy-Gewichten - er kann bei knapp
gleichauf liegenden Ergebnissen den Ausschlag geben, aber nie
einen inhaltlich schwaecheren Treffer nach vorne katapultieren.

Getrennt von Entry (Nutzerdaten) und Analysis (Discovery-Daten) -
das hier ist eine dritte, eigene Kategorie: Verhaltensdaten.
"""

from __future__ import annotations

from collections import defaultdict
from uuid import UUID

MAX_BEHAVIOR_BONUS = 0.3  # bewusst klein, siehe Docstring oben


class BehaviorMemory:

    def __init__(self) -> None:
        # (normalisierter query-text) -> {entry_id: mal_ausgewaehlt}
        self._selections: dict[str, dict[UUID, int]] = defaultdict(lambda: defaultdict(int))

    def record_selection(self, query: str, entry_id: UUID) -> None:
        key = query.strip().lower()
        self._selections[key][entry_id] += 1

    def bonus_for(self, query: str, entry_id: UUID) -> float:
        key = query.strip().lower()
        counts = self._selections.get(key)
        if not counts:
            return 0.0

        total = sum(counts.values())
        this_entry = counts.get(entry_id, 0)
        if total == 0:
            return 0.0

        # Anteil, wie oft DIESER Entry bei DIESER Query gewaehlt wurde,
        # skaliert auf den gedeckelten Maximalbonus.
        ratio = this_entry / total
        return ratio * MAX_BEHAVIOR_BONUS
