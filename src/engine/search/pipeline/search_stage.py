"""
KIVO Search Engine
Search Stage

Aufgabe: Titel + Inhalt aller Entries durchsuchen (exakt, prefix,
synonym, fuzzy) und Rohtreffer sammeln. Kein Ranking hier.
"""

from __future__ import annotations

from ..pipeline.tokenizer import Tokenizer
from ..pipeline.normalizer import Normalizer
from ..pipeline.stopwords import STOPWORDS
from ..pipeline.fuzzy import best_fuzzy_match
from ..text_cleaning import strip_media

MIN_PREFIX_LENGTH = 4  # ab dieser Laenge zaehlt "konfig" -> "konfiguration" als Treffer


class SearchStage:

    def __init__(self, repository, synonyms=None, stopwords=None, normalizer=None) -> None:
        self._repository = repository
        self._synonyms = synonyms
        self._tokenizer = Tokenizer()
        self._normalizer = normalizer if normalizer is not None else Normalizer()
        self._stopwords = stopwords if stopwords is not None else STOPWORDS

    def execute(self, context) -> None:
        query_terms = context.normalized_tokens or context.filtered_tokens
        # Fuer den Phrase-Bonus: die Query als zusammenhaengender Text, roh
        phrase = " ".join(context.filtered_tokens).strip()

        for entry in self._repository.get_all():
            title_tokens = self._normalized_tokens(entry.title)
            content_tokens = self._normalized_tokens(entry.content)
            all_tokens = set(title_tokens) | set(content_tokens)

            title_hits = 0
            content_hits = 0
            prefix_hits: list[str] = []
            synonym_hits: list[tuple[str, str]] = []
            fuzzy_hits: list[tuple[str, str, float]] = []

            for term in query_terms:
                if term in title_tokens:
                    title_hits += title_tokens.count(term)
                    continue
                if term in content_tokens:
                    content_hits += content_tokens.count(term)
                    continue

                if len(term) >= MIN_PREFIX_LENGTH:
                    prefix_match = next(
                        (t for t in all_tokens if len(t) >= MIN_PREFIX_LENGTH and (t.startswith(term) or term.startswith(t))),
                        None,
                    )
                    if prefix_match:
                        prefix_hits.append(term)
                        continue

                if self._synonyms is not None:
                    expanded = self._synonyms.expand(term) - {term}
                    matched_synonym = next((s for s in expanded if s in all_tokens), None)
                    if matched_synonym:
                        synonym_hits.append((term, matched_synonym))
                        continue

                match = best_fuzzy_match(term, list(all_tokens))
                if match:
                    fuzzy_hits.append((term, match[0], match[1]))

            # Phrase-Bonus: die komplette (gesaeuberte) Query kommt woertlich
            # als Teilstring in Titel/Inhalt vor - sehr starkes Signal
            phrase_match = bool(phrase) and len(phrase) >= 6 and (
                phrase in entry.title.lower() or phrase in entry.content.lower()
            )

            if title_hits or content_hits or prefix_hits or synonym_hits or fuzzy_hits or phrase_match:
                context.candidates[entry.id] = {
                    "entry": entry,
                    "title_hits": title_hits,
                    "content_hits": content_hits,
                    "prefix_hits": prefix_hits,
                    "synonym_hits": synonym_hits,
                    "fuzzy_hits": fuzzy_hits,
                    "phrase_match": phrase_match,
                }

    def _normalized_tokens(self, text: str) -> list[str]:
        text = strip_media(text)
        tokens = [t for t in self._tokenizer.tokenize(text) if t not in self._stopwords]
        return [self._normalizer.normalize(t) for t in tokens]
