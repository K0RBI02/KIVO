"""
KIVO Search Engine
Link

Zwei Arten: manuell (vom Nutzer gesetzt) und suggested (automatisch berechnet).
Reihenfolge ist immer: erst manuelle Links, dann Vorschlaege. Maximal 3 gesamt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

LinkKind = Literal["manual", "suggested"]


@dataclass(slots=True, frozen=True)
class Link:
    target_id: UUID
    kind: LinkKind
    score: float = 0.0  # nur relevant fuer "suggested", zum Ranking


def combine_links(manual: list[Link], suggested: list[Link], max_total: int = 3) -> list[Link]:
    """
    Regel aus der Spec:
      0 manuelle  -> 3 Vorschlaege
      1 manuelle  -> 1 manuell + 2 Vorschlaege
      2 manuelle  -> 2 manuell + 1 Vorschlag
      3+ manuelle -> nur die manuellen, 0 Vorschlaege
    Manuelle Links kommen immer zuerst.
    """
    manual = manual[:max_total]
    remaining_slots = max(0, max_total - len(manual))

    # Vorschlaege sortiert nach Score (bester zuerst), Duplikate zu manuellen raus
    manual_targets = {l.target_id for l in manual}
    ranked_suggestions = sorted(
        (s for s in suggested if s.target_id not in manual_targets),
        key=lambda s: s.score,
        reverse=True,
    )

    return manual + ranked_suggestions[:remaining_slots]
