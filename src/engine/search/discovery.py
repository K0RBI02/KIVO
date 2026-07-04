"""
KIVO Search Engine
Discovery

Die groesste Architekturentscheidung aus der Spec: die Engine besitzt
KEIN eingebautes Weltwissen. Sie beobachtet, welche Begriffe in mehreren
Entries auftauchen, und erklaert die selbst zu "Konzepten".

Kein Docker/Caddy/Kubernetes-Woerterbuch - das entsteht rein aus den
Daten des Nutzers.
"""

from __future__ import annotations

from .entry import Entry
from .analysis import Analysis, ConceptStats
from .pipeline.tokenizer import Tokenizer
from .pipeline.normalizer import Normalizer


def discover(entries: tuple[Entry, ...]) -> Analysis:
    """Baut eine komplett neue Analysis aus dem aktuellen Entry-Bestand."""

    tokenizer = Tokenizer()
    normalizer = Normalizer()

    analysis = Analysis()
    analysis._total_documents = len(entries)

    for entry in entries:
        text = f"{entry.title} {entry.content}"
        raw_tokens = tokenizer.tokenize(text)
        filtered = [t for t in raw_tokens if t not in _stopwords()]
        normalized = [normalizer.normalize(t) for t in filtered]

        seen_in_this_entry: set[str] = set()

        for term in normalized:
            if len(term) < 2:
                continue

            stats = analysis.concepts.setdefault(term, ConceptStats(term=term))
            stats.total_frequency += 1

            if term not in seen_in_this_entry:
                stats.document_frequency += 1
                stats.entry_ids.add(entry.id)
                seen_in_this_entry.add(term)

    return analysis


def _stopwords():
    from .pipeline.stopwords import STOPWORDS
    return STOPWORDS
