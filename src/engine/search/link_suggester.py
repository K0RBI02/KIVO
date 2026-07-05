"""
KIVO Search Engine
Link Suggester

Berechnet automatische Link-Vorschlaege ueber den Knowledge Graph
(gemeinsame entdeckte Konzepte). Nutzer sieht den Graphen nie - nur
die fertigen Vorschlaege, kombiniert mit manuellen Links nach der
Regel aus link.py (max 3, manuelle zuerst).
"""

from __future__ import annotations

from .entry import Entry
from .link import Link, combine_links
from .graph import KnowledgeGraph
from .pipeline.tokenizer import Tokenizer
from .pipeline.normalizer import Normalizer
from .pipeline.stopwords import STOPWORDS
from .text_cleaning import strip_media


def suggest_links(entry: Entry, all_entries: tuple[Entry, ...], analysis, graph: KnowledgeGraph, max_total: int = 3, stopwords: set[str] | None = None, normalizer=None) -> list[Link]:
    tokenizer = Tokenizer()
    active_normalizer = normalizer if normalizer is not None else Normalizer()
    active_stopwords = stopwords if stopwords is not None else STOPWORDS

    text = strip_media(f"{entry.title} {entry.content}")
    tokens = [t for t in tokenizer.tokenize(text) if t not in active_stopwords]
    concept_terms = {active_normalizer.normalize(t) for t in tokens}
    concept_terms = {t for t in concept_terms if analysis.is_known_concept(t)}

    # score pro anderem Entry = Anzahl gemeinsamer entdeckter Konzepte
    scores: dict = {}

    for other in all_entries:
        if other.id == entry.id:
            continue

        other_text = strip_media(f"{other.title} {other.content}")
        other_tokens = [t for t in tokenizer.tokenize(other_text) if t not in active_stopwords]
        other_terms = {active_normalizer.normalize(t) for t in other_tokens}

        shared = concept_terms & other_terms
        if shared:
            scores[other.id] = float(len(shared))

    suggested = [
        Link(target_id=other_id, kind="suggested", score=score)
        for other_id, score in scores.items()
    ]

    return combine_links(entry.manual_links, suggested, max_total=max_total)
