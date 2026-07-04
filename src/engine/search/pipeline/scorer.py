"""
KIVO Search Engine
Scorer

Prioritaet laut Spec (Reihenfolge = Gewichtung, absteigend):
  1. Titel
  2. Inhalt
  3. erkannte Keywords (Konzept-Bonus)
  4. Fuzzy Matching
  5. Synonyme
  6. manuelle Links       (hier nicht relevant, betrifft link_suggester.py)
  7. Benutzerverhalten    (Bonus - darf NIE einen besseren Treffer ueberholen)
  8. Aktualitaet          (Bonus)
"""

from __future__ import annotations

from datetime import datetime, timezone

TITLE_WEIGHT = 5.0
CONTENT_WEIGHT = 2.0
FUZZY_WEIGHT = 1.5
SYNONYM_WEIGHT = 1.0
RECENCY_MAX_BONUS = 0.5   # klein: darf nie einen inhaltlich besseren Treffer schlagen


class Scorer:

    def __init__(self, behavior=None) -> None:
        self._behavior = behavior

    def execute(self, context) -> None:
        for entry_id, candidate in context.candidates.items():
            score = 0.0

            score += candidate["title_hits"] * TITLE_WEIGHT
            score += candidate["content_hits"] * CONTENT_WEIGHT

            for _term, _matched, ratio in candidate["fuzzy_hits"]:
                score += ratio * FUZZY_WEIGHT

            score += len(candidate["synonym_hits"]) * SYNONYM_WEIGHT

            # Konzept-Bonus: Query-Begriffe, die die Engine als "Konzept" kennt
            concept_bonus = 0.0
            title_lower = candidate["entry"].title.lower()
            content_lower = candidate["entry"].content.lower()
            for term in context.normalized_tokens:
                if term in title_lower or term in content_lower:
                    concept_bonus += context.weighted_tokens.get(term, 1.0) - 1.0
            score += concept_bonus

            score += self._recency_bonus(candidate["entry"].last_modified)

            if self._behavior is not None:
                score += self._behavior.bonus_for(context.raw_query, entry_id)

            context.scores[entry_id] = score

    def _recency_bonus(self, last_modified: datetime) -> float:
        age_days = (datetime.now(timezone.utc) - last_modified).days
        if age_days <= 0:
            return RECENCY_MAX_BONUS
        return max(0.0, RECENCY_MAX_BONUS * (1 - age_days / 30))
