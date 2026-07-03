"""
KIVO Search Engine
Analysis

Enthaelt AUSSCHLIESSLICH berechnete Daten (Self-Discovery-Ergebnisse).
Keine Nutzerdaten. Darf jederzeit geloescht und neu berechnet werden -
strikte Trennung von Entry (Nutzerdaten) und Analysis (Engine-Daten).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class ConceptStats:
    """Ein von der Engine selbst entdeckter Begriff (kein eingebautes Wissen)."""

    term: str
    document_frequency: int = 0          # in wie vielen Entries kommt der Begriff vor
    total_frequency: int = 0             # wie oft insgesamt
    entry_ids: set[UUID] = field(default_factory=set)

    @property
    def is_concept(self) -> bool:
        """Ein Begriff gilt erst als 'Konzept', wenn er in >=2 Entries auftaucht."""
        return self.document_frequency >= 2


@dataclass(slots=True)
class Analysis:
    """
    Recomputable Snapshot der Self-Discovery.
    engine.rebuild_analysis() erzeugt eine neue Instanz - nichts hier
    wird persistiert, nichts hier ist Nutzerdatum.
    """

    concepts: dict[str, ConceptStats] = field(default_factory=dict)

    def is_known_concept(self, term: str) -> bool:
        stats = self.concepts.get(term)
        return stats is not None and stats.is_concept

    def concept_weight(self, term: str) -> float:
        """Je seltener/spezifischer ein entdeckter Begriff, desto staerker sein Gewicht (idf-artig)."""
        stats = self.concepts.get(term)
        if stats is None or stats.document_frequency == 0:
            return 1.0

        # idf-aehnlich: haeufige Begriffe (in vielen Entries) weniger unterscheidungskraeftig
        import math
        total_docs = max(1, self._total_documents)
        return 1.0 + math.log((total_docs + 1) / (stats.document_frequency + 1))

    _total_documents: int = 0
