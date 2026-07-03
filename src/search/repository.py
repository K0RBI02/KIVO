"""
KIVO Search Engine
Entry Repository

Reine Persistenz. Kein Ranking, kein Scoring, keine Business-Logik.
'search' hier ist ein einfacher Rohzugriff (Substring-Filter), NICHT
die vom Client aufgerufene, gerankte Suche - die laeuft immer ueber
die Pipeline in engine.py.
"""

from __future__ import annotations

from uuid import UUID

from .entry import Entry


class EntryRepository:

    def __init__(self) -> None:
        self._entries: dict[UUID, Entry] = {}

    def create(self, entry: Entry) -> Entry:
        self._entries[entry.id] = entry
        return entry

    def update(self, entry: Entry) -> Entry:
        entry.touch()
        self._entries[entry.id] = entry
        return entry

    def delete(self, entry_id: UUID) -> None:
        self._entries.pop(entry_id, None)

    def get(self, entry_id: UUID) -> Entry | None:
        return self._entries.get(entry_id)

    def get_all(self) -> tuple[Entry, ...]:
        return tuple(self._entries.values())

    def search(self, term: str) -> tuple[Entry, ...]:
        """Roh-Substring-Suche ueber Titel + Inhalt (case-insensitive)."""
        term = term.lower()
        return tuple(
            e for e in self._entries.values()
            if term in e.title.lower() or term in e.content.lower()
        )
