"""
KIVO Search Engine
Search Stage

Aufgabe: Titel + Inhalt aller Entries durchsuchen (exakt + fuzzy)
und Rohtreffer sammeln. Kein Ranking hier - nur Kandidaten sammeln.
"""

from __future__ import annotations

from ..pipeline.tokenizer import Tokenizer
from ..pipeline.normalizer import Normalizer
from ..pipeline.stopwords import STOPWORDS
from ..pipeline.fuzzy import best_fuzzy_match


class SearchStage:

    def __init__(self, repository) -> None:
        self._repository = repository
        self._tokenizer = Tokenizer()
        self._normalizer = Normalizer()

    def execute(self, context) -> None:
        query_terms = context.normalized_tokens or context.filtered_tokens

        for entry in self._repository.get_all():
            title_tokens = self._normalized_tokens(entry.title)
            content_tokens = self._normalized_tokens(entry.content)
            all_tokens = set(title_tokens) | set(content_tokens)

            title_hits = 0
            content_hits = 0
            fuzzy_hits: list[tuple[str, str, float]] = []

            for term in query_terms:
                if term in title_tokens:
                    title_hits += title_tokens.count(term)
                elif term in content_tokens:
                    content_hits += content_tokens.count(term)
                else:
                    match = best_fuzzy_match(term, list(all_tokens))
                    if match:
                        fuzzy_hits.append((term, match[0], match[1]))

            if title_hits or content_hits or fuzzy_hits:
                context.candidates[entry.id] = {
                    "entry": entry,
                    "title_hits": title_hits,
                    "content_hits": content_hits,
                    "fuzzy_hits": fuzzy_hits,
                }

    def _normalized_tokens(self, text: str) -> list[str]:
        tokens = [t for t in self._tokenizer.tokenize(text) if t not in STOPWORDS]
        return [self._normalizer.normalize(t) for t in tokens]
