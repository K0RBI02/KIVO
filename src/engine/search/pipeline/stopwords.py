"""
KIVO Search Engine
Stopword Filter

Aufgabe: haeufige Fuellwoerter entfernen. Sprachabhaengig (siehe Spec).
Aktuell: Deutsch + etwas Englisch als Startset, spaeter pro Sprache
austauschbar (Modul wird ERSETZT, nicht die Pipeline umgebaut).
"""

from __future__ import annotations

GERMAN_STOPWORDS = {
    "der", "die", "das", "und", "oder", "ist", "war", "wie", "was", "wo",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich", "mir", "dir",
    "mit", "auf", "fuer", "für", "von", "zu", "im", "in", "ein", "eine",
    "einen", "einem", "einer", "hab", "habe", "hatte", "hatten", "nicht",
    "auch", "mal", "dieses", "diese", "dieser", "noch", "so", "als", "an",
    "am", "bei", "aus", "nach", "ueber", "über", "unter", "durch", "um",
    "ohne", "gegen", "bis", "seit", "nochmal", "nochmals", "wieder", "man",
    "kann", "muss", "soll", "wird", "werden", "sein", "haben", "dann",
}

ENGLISH_STOPWORDS = {
    "the", "a", "an", "is", "was", "how", "what", "where", "i", "you",
    "he", "she", "it", "we", "they", "with", "on", "for", "of", "to",
    "in", "not", "also", "again", "this", "that", "these", "those",
    "can", "must", "should", "will", "be", "have", "then", "my", "me",
}

STOPWORDS = GERMAN_STOPWORDS | ENGLISH_STOPWORDS


class StopwordFilter:

    def execute(self, context) -> None:
        context.filtered_tokens = [t for t in context.tokens if t not in STOPWORDS]
