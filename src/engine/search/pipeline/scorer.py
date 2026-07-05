"""
KIVO Search Engine
Scorer

Prioritaet laut Spec (absteigend):
  1. Titel
  2. Inhalt
  3. erkannte Keywords (Konzept-Bonus)
  4. Fuzzy Matching / Prefix
  5. Synonyme
  6. manuelle Links       (betrifft link_suggester.py, nicht hier)
  7. Benutzerverhalten    (Bonus - darf NIE einen besseren Treffer ueberholen)
  8. Aktualitaet          (Bonus)

WICHTIG: Zaehlungen werden log-gedaempft (log1p), sonst gewinnt automatisch
die laengste Notiz mit den meisten Wortwiederholungen, unabhaengig von
Relevanz. Ein Wort 1x vs 2x im Titel soll einen kleinen, keinen linearen
Unterschied machen.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

TITLE_WEIGHT = 5.0
CONTENT_WEIGHT = 2.0
PREFIX_WEIGHT = 1.8
FUZZY_WEIGHT = 1.5
SYNONYM_WEIGHT = 1.0
PHRASE_BONUS = 3.0
RECENCY_MAX_BONUS = 0.5


class Scorer:

    def __init__(self, behavior=None) -> None:
        self._behavior = behavior

    def execute(self, context) -> None:
        for entry_id, candidate in context.candidates.items():
            score = 0.0

            score += math.log1p(candidate["title_hits"]) * TITLE_WEIGHT
            score += math.log1p(candidate["content_hits"]) * CONTENT_WEIGHT
            score += len(candidate["prefix_hits"]) * PREFIX_WEIGHT
            score += len(candidate["synonym_hits"]) * SYNONYM_WEIGHT

            for _term, _matched, ratio in candidate["fuzzy_hits"]:
                score += ratio * FUZZY_WEIGHT

            if candidate.get("phrase_match"):
                score += PHRASE_BONUS

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
