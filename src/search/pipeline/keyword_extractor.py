"""
KIVO Search Engine
Keyword Extractor

Aufgabe: Query-Tokens gewichten. Bekannte "Konzepte" (von der Discovery
entdeckt) bekommen mehr Gewicht als Zufallswoerter.
"""

from __future__ import annotations


class KeywordExtractor:

    def __init__(self, analysis) -> None:
        self._analysis = analysis

    def execute(self, context) -> None:
        weighted = {}
        for term in context.normalized_tokens:
            weighted[term] = self._analysis.concept_weight(term)
        context.weighted_tokens = weighted
