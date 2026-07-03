"""
KIVO Search Engine
Scorer

Prioritaet laut Spec (Reihenfolge = Gewichtung):
  1. Titel
  2. Inhalt
  3. erkannte Keywords (Konzept-Bonus)
  4. Fuzzy Matching
  5. Synonyme        (Hook fuer spaeter, hier noch neutral)
  6. manuelle Links   (Hook fuer spaeter)
  7. Benutzerverhalten (Bonus - darf NIE einen besseren Treffer ueberholen)
  8. Aktualitaet      (Bonus)
"""

from __future__ import annotations

from datetime import datetime, timezone

TITLE_WEIGHT = 5.0
CONTENT_WEIGHT = 2.0
FUZZY_WEIGHT = 1.5
RECENCY_MAX_BONUS = 0.5  # bewusst klein: darf nie einen inhaltlich besseren Treffer schlagen


class Scorer:

    def execute(self, context) -> None:
        for entry_id, candidate in context.candidates.items():
            score = 0.0

            score += candidate["title_hits"] * TITLE_WEIGHT
            score += candidate["content_hits"] * CONTENT_WEIGHT

            for term, _matched, ratio in candidate["fuzzy_hits"]:
                score += ratio * FUZZY_WEIGHT

            # Konzept-Bonus: Query-Begriffe, die die Engine als "Konzept" kennt,
            # zaehlen mehr (siehe KeywordExtractor / context.weighted_tokens)
            concept_bonus = 0.0
            for term in context.normalized_tokens:
                if term in candidate["entry"].title.lower() or term in candidate["entry"].content.lower():
                    concept_bonus += context.weighted_tokens.get(term, 1.0) - 1.0
            score += concept_bonus

            score += self._recency_bonus(candidate["entry"].last_modified)

            context.scores[entry_id] = score

    def _recency_bonus(self, last_modified: datetime) -> float:
        age_days = (datetime.now(timezone.utc) - last_modified).days
        if age_days <= 0:
            return RECENCY_MAX_BONUS
        # linear abklingend, nach 30 Tagen kein Bonus mehr
        return max(0.0, RECENCY_MAX_BONUS * (1 - age_days / 30))
