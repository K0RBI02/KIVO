"""
KIVO Search Engine
Knowledge Graph

Der Nutzer sieht diesen Graphen NIE (siehe Spec). Er dient nur intern
dazu, Link-Vorschlaege und verwandte Konzepte zu berechnen.

Wiederverwendet bewusst den bestehenden Node/Relation-Kern der Engine:
  Node     = ein entdecktes Konzept (Keyword)
  Relation = "kommt gemeinsam vor" zwischen zwei Konzepten, Gewicht = Haeufigkeit
"""

from __future__ import annotations

from domain.manager import DomainManager
from domain.node import Node
from domain.relation import Relation
from domain.types import RelationType
from core.event_bus import EventBus

from .analysis import Analysis
from .entry import Entry


class KnowledgeGraph:

    def __init__(self) -> None:
        self._event_bus = EventBus()
        self.domain = DomainManager(self._event_bus)
        self._node_by_term: dict[str, Node] = {}

    def node_for(self, term: str) -> Node | None:
        return self._node_by_term.get(term)

    def connected_terms(self, term: str) -> list[tuple[str, float]]:
        """Liefert verwandte Begriffe + Kantengewicht, staerkste zuerst."""
        node = self._node_by_term.get(term)
        if node is None:
            return []

        results = []
        for relation in self.domain.relations():
            if relation.source_id == node.id:
                other = self.domain.get_node(relation.target_id)
                results.append((other.name, relation.weight))
            elif relation.target_id == node.id:
                other = self.domain.get_node(relation.source_id)
                results.append((other.name, relation.weight))

        results.sort(key=lambda pair: pair[1], reverse=True)
        return results

    def _get_or_create_node(self, term: str) -> Node:
        node = self._node_by_term.get(term)
        if node is not None:
            return node

        node = Node(name=term)
        self.domain.add_node(node)
        self._node_by_term[term] = node
        return node

    def _connect(self, term_a: str, term_b: str) -> None:
        node_a = self._get_or_create_node(term_a)
        node_b = self._get_or_create_node(term_b)

        for relation in self.domain.relations():
            if relation.contains(node_a.id, node_b.id) or relation.contains(node_b.id, node_a.id):
                relation.weight += 1.0
                return

        self.domain.add_relation(
            Relation(
                source_id=node_a.id,
                target_id=node_b.id,
                type=RelationType.LINK,
                weight=1.0,
                directed=False,
            )
        )


def build_graph(entries: tuple[Entry, ...], analysis: Analysis) -> KnowledgeGraph:
    """
    Baut den Graphen komplett neu aus dem aktuellen Wissen.
    Nur echte 'Konzepte' (>=2 Entries) werden zu Knoten - einzelne
    Zufallswoerter erzeugen keinen Graph-Laerm.
    """

    from .pipeline.tokenizer import Tokenizer
    from .pipeline.normalizer import Normalizer
    from .pipeline.stopwords import STOPWORDS

    tokenizer = Tokenizer()
    normalizer = Normalizer()
    graph = KnowledgeGraph()

    for entry in entries:
        text = f"{entry.title} {entry.content}"
        tokens = tokenizer.tokenize(text)
        filtered = [t for t in tokens if t not in STOPWORDS]
        normalized = {normalizer.normalize(t) for t in filtered}

        concept_terms = sorted(t for t in normalized if analysis.is_known_concept(t))

        for i in range(len(concept_terms)):
            for j in range(i + 1, len(concept_terms)):
                graph._connect(concept_terms[i], concept_terms[j])

    return graph
