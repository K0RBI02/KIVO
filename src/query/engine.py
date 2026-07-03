"""
KIVO Engine
Query Engine

EINZIGE QueryEngine im Projekt. Vorher gab es zwei parallele
Implementierungen (core/query_engine.py und query/engine.py) -
das ist jetzt zusammengefuehrt:
  - find_by_name / find_by_tag / find_by_property_key: direkte Domain-Queries
  - search / filter: generische Textsuche & Filterung
  - rebuild_index / indexed_search: schnelle Lookups ueber einen Index
"""

from __future__ import annotations

from typing import Any, Iterable

from domain.node import Node
from domain.manager import DomainManager

from .filter import Filter
from .index import Index
from .search import Search


class QueryEngine:

    def __init__(self, domain: DomainManager) -> None:
        self.domain = domain
        self.searcher = Search()
        self.index = Index()

    # -------- direkte Domain-Queries --------

    def find_by_name(self, name: str) -> tuple[Node, ...]:
        return tuple(node for node in self.domain.nodes() if node.name == name)

    def find_by_tag(self, tag: str) -> tuple[Node, ...]:
        return tuple(node for node in self.domain.nodes() if node.has_tag(tag))

    def find_by_property_key(self, key: str) -> tuple[Node, ...]:
        return tuple(node for node in self.domain.nodes() if node.has_property(key))

    # -------- generische Textsuche & Filter --------

    def search(self, term: str, items: Iterable[Any] | None = None) -> list[Any]:
        """Textsuche. Ohne 'items' wird ueber alle Nodes gesucht."""
        return self.searcher.find(items if items is not None else self.domain.nodes(), term)

    def filter(self, filters: list[Filter], items: Iterable[Any] | None = None) -> list[Any]:
        source = items if items is not None else self.domain.nodes()
        return [item for item in source if all(f.matches(item) for f in filters)]

    # -------- Index (fuer haeufige Lookups) --------

    def rebuild_index(self) -> None:
        self.index.clear()
        self.index.build(list(self.domain.nodes()))

    def indexed_search(self, term: str) -> set:
        return self.index.search(term.lower())
