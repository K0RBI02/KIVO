"""
KIVO Search Engine
Sprachunterstuetzung

Architekturentscheidung: KEIN Hard-Dependency auf ein NLP-Paket.
Falls 'snowballstemmer' installiert ist (reines Python, keine grossen
Sprachmodelle, pip install snowballstemmer), wird es automatisch fuer
bessere Stemming-Qualitaet genutzt. Ist es nicht installiert, faellt
die Engine auf den eingebauten Heuristik-Normalizer zurueck - die App
funktioniert so oder so, wird mit der Bibliothek nur praeziser.

Warum snowballstemmer und nicht z.B. NLTK/spaCy:
  - reines Python, keine Bibliotheks-Sprachmodelle zum Herunterladen
  - deckt >15 Sprachen ab (de, en, fr, es, it, ...) mit derselben API
  - Installationsgroesse: < 1 MB statt hunderte MB bei spaCy-Modellen
"""

from __future__ import annotations

from .pipeline.stopwords import GERMAN_STOPWORDS, ENGLISH_STOPWORDS, STOPWORDS
from .pipeline.normalizer import Normalizer as HeuristicNormalizer

try:
    import snowballstemmer
    _HAS_SNOWBALL = True
except ImportError:
    _HAS_SNOWBALL = False

_SNOWBALL_LANG_MAP = {
    "de": "german",
    "en": "english",
}

_STOPWORDS_BY_LANG = {
    "de": GERMAN_STOPWORDS,
    "en": ENGLISH_STOPWORDS,
    "auto": STOPWORDS,  # gemischt, aktueller Default-Modus
}


class StemmerNormalizer:
    """Adapter, damit snowballstemmer dieselbe .normalize()-Schnittstelle hat."""

    def __init__(self, lang: str) -> None:
        self._stemmer = snowballstemmer.stemmer(_SNOWBALL_LANG_MAP[lang])

    def normalize(self, token: str) -> str:
        return self._stemmer.stemWord(token.lower())


def available_languages() -> list[str]:
    return ["auto", "de", "en"]


def stopwords_for(lang: str) -> set[str]:
    return _STOPWORDS_BY_LANG.get(lang, STOPWORDS)


def normalizer_for(lang: str):
    """
    Liefert das beste verfuegbare Normalizer-Objekt fuer eine Sprache.
    'auto' und unbekannte Sprachen nutzen immer den Heuristik-Normalizer
    (funktioniert gemischt DE/EN, wie bisher).
    """
    if lang in _SNOWBALL_LANG_MAP and _HAS_SNOWBALL:
        return StemmerNormalizer(lang)
    return HeuristicNormalizer()


def snowball_available() -> bool:
    return _HAS_SNOWBALL


def detect_language(tokens: list[str]) -> str:
    """Ganz einfache Heuristik: welche Stopword-Liste passt besser?"""
    if not tokens:
        return "auto"

    de_hits = sum(1 for t in tokens if t in GERMAN_STOPWORDS)
    en_hits = sum(1 for t in tokens if t in ENGLISH_STOPWORDS)

    if de_hits == 0 and en_hits == 0:
        return "auto"

    return "de" if de_hits >= en_hits else "en"
