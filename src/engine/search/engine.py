"""
KIVO Search Engine
KnowledgeEngine

Die EINZIGE Anlaufstelle fuer jeden Client (Desktop, Mobile, CLI,
Browser, API). Clients duerfen niemals selbst suchen, ranken, sortieren
oder Empfehlungen berechnen - sie rufen ausschliesslich diese Fassade auf.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from .entry import Entry
from .link import Link
from .repository import EntryRepository
from .analysis import Analysis
from .discovery import discover
from .graph import KnowledgeGraph, build_graph
from .link_suggester import suggest_links
from .synonyms import SynonymDictionary
from .learning import BehaviorMemory
from .persistence import EntryStore

from .pipeline.pipeline import Pipeline
from .pipeline.tokenizer import Tokenizer
from .pipeline.stopwords import StopwordFilter
from .pipeline.normalizer import Normalizer
from .pipeline.keyword_extractor import KeywordExtractor
from .pipeline.search_stage import SearchStage
from .pipeline.scorer import Scorer
from .pipeline.result_builder import ResultBuilder, SearchResult


class KnowledgeEngine:

    def __init__(self, data_dir: str | Path = "kivo_data", auto_save: bool = True) -> None:
        self.repository = EntryRepository()
        self.analysis = Analysis()
        self.graph = KnowledgeGraph()
        self.synonyms = SynonymDictionary()
        self.behavior = BehaviorMemory()

        self._auto_save = auto_save
        self._store = EntryStore(data_dir)

        self._load_from_disk()

    # -------- Persistenz --------

    def _load_from_disk(self) -> None:
        entries = self._store.load_all()
        for entry in entries:
            self.repository.create(entry)
        self.rebuild_analysis()

    def save(self) -> None:
        self._store.save_all(self.repository.get_all())

    def _maybe_save(self) -> None:
        if self._auto_save:
            self.save()

    # -------- CRUD (kein Client baut das selbst) --------

    def create(self, title: str, content: str) -> Entry:
        entry = Entry(title=title, content=content)
        self.repository.create(entry)
        self.rebuild_analysis()
        self._maybe_save()
        return entry

    def update(self, entry_id: UUID, *, title: str | None = None, content: str | None = None) -> Entry | None:
        entry = self.repository.get(entry_id)
        if entry is None:
            return None
        if title is not None:
            entry.title = title
        if content is not None:
            entry.content = content
        self.repository.update(entry)
        self.rebuild_analysis()
        self._maybe_save()
        return entry

    def delete(self, entry_id: UUID) -> None:
        self.repository.delete(entry_id)
        self.rebuild_analysis()
        self._maybe_save()

    def get(self, entry_id: UUID) -> Entry | None:
        return self.repository.get(entry_id)

    def get_all(self) -> tuple[Entry, ...]:
        return self.repository.get_all()

    def recent(self, limit: int = 5) -> tuple[Entry, ...]:
        """
        Zuletzt geaenderte Entries - fuer die Startansicht (leere Suche).
        Bewusst hier in der Engine, nicht im Client: Clients sortieren nie selbst.
        """
        ordered = sorted(self.repository.get_all(), key=lambda e: e.last_modified, reverse=True)
        return tuple(ordered[:limit])

    def link(self, entry_id: UUID, target_id: UUID) -> None:
        entry = self.repository.get(entry_id)
        if entry is None:
            return
        entry.add_manual_link(target_id)
        self.repository.update(entry)
        self._maybe_save()

    # -------- Self-Discovery (rein Engine-intern) --------

    def rebuild_analysis(self) -> None:
        self.analysis = discover(self.repository.get_all())
        self.graph = build_graph(self.repository.get_all(), self.analysis)

    # -------- Die Suche - das Herz des Produkts --------

    def search(self, query: str) -> list[SearchResult]:
        pipeline = Pipeline([
            Tokenizer(),
            StopwordFilter(),
            Normalizer(),
            KeywordExtractor(self.analysis),
            SearchStage(self.repository, synonyms=self.synonyms),
            Scorer(behavior=self.behavior),
            ResultBuilder(),
        ])

        context = pipeline.run(query)
        return context.results

    def record_selection(self, query: str, entry_id: UUID) -> None:
        """Client meldet: Nutzer hat bei dieser Suche dieses Ergebnis gewaehlt."""
        self.behavior.record_selection(query, entry_id)

    # -------- Links (manuell + automatisch) --------

    def links_for(self, entry_id: UUID, max_total: int = 3) -> list[Link]:
        entry = self.repository.get(entry_id)
        if entry is None:
            return []
        return suggest_links(entry, self.repository.get_all(), self.analysis, self.graph, max_total=max_total)

    def related_concepts(self, term: str) -> list[tuple[str, float]]:
        return self.graph.connected_terms(term)
