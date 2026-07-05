"""
KIVO Search Engine
Normalizer

Aufgabe: Woerter vereinheitlichen (installieren/Installation -> install).
Heuristischer Leicht-Stemmer, kein Woerterbuch (Self-Discovery-Prinzip:
die Engine soll kein Weltwissen brauchen). Sprachabhaengig, austauschbar.
"""

from __future__ import annotations

# Reihenfolge wichtig: laengere/speziellere Endungen zuerst pruefen,
# sonst wird zu frueh (und falsch) gekuerzt.
_GERMAN_SUFFIXES = [
    "ierungen", "ierung", "ationen", "ation", "ieren", "iert",
    "ungen", "ung", "heiten", "heit", "keiten", "keit",
    "en", "er", "es", "e", "s",
]

_MIN_STEM_LENGTH = 3


class Normalizer:

    def execute(self, context) -> None:
        context.normalized_tokens = [self.normalize(t) for t in context.filtered_tokens]

    @staticmethod
    def normalize(token: str) -> str:
        word = token.lower()

        for suffix in _GERMAN_SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= _MIN_STEM_LENGTH:
                return word[: -len(suffix)]

        return word


class NormalizerStage:
    """
    Adapter: macht aus JEDEM Objekt mit .normalize(word) eine Pipeline-Stufe.
    Damit kann engine.py wahlweise den Heuristik-Normalizer oder einen
    echten Sprach-Stemmer (siehe language.py) in dieselbe Pipeline stecken,
    ohne die Pipeline selbst anzufassen.
    """

    def __init__(self, normalizer) -> None:
        self._normalizer = normalizer

    def execute(self, context) -> None:
        context.normalized_tokens = [self._normalizer.normalize(t) for t in context.filtered_tokens]
