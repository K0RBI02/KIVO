"""
KIVO Search Engine
Fuzzy Matching

Kein externes Paket noetig - difflib aus der Stdlib reicht fuer
Tippfehler- und Bruchstueck-Toleranz ("Proxy-Dings" -> "Proxy").
"""

from __future__ import annotations

from difflib import SequenceMatcher

DEFAULT_THRESHOLD = 0.72
MIN_LENGTH_FOR_FUZZY = 4  # kurze Woerter (z.B. "is", "ich") erzeugen sonst Zufallstreffer


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def best_fuzzy_match(token: str, candidates: list[str], threshold: float = DEFAULT_THRESHOLD) -> tuple[str, float] | None:
    """Bestes Fuzzy-Match aus einer Kandidatenliste, oder None."""
    if len(token) < MIN_LENGTH_FOR_FUZZY:
        return None

    best_word = None
    best_score = 0.0

    for candidate in candidates:
        if len(candidate) < MIN_LENGTH_FOR_FUZZY:
            continue
        score = similarity(token, candidate)
        if score > best_score:
            best_score = score
            best_word = candidate

    if best_word is not None and best_score >= threshold:
        return best_word, best_score

    return None
