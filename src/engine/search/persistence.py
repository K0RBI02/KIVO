"""
KIVO Search Engine
Persistence

Nutzt bewusst die bereits vorhandene storage/-Schicht (FileStorage +
JsonSerializer) - kein neues Rad erfunden. Speichert NUR Entries
(Nutzerdaten). Analysis/Graph sind Engine-Daten und werden nie
persistiert, sondern nach dem Laden neu berechnet.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID
from datetime import datetime

from storage.file_storage import FileStorage
from storage.serializer import JsonSerializer

from .entry import Entry
from .link import Link


class EntryStore:

    def __init__(self, directory: str | Path = "kivo_data") -> None:
        self._storage = FileStorage(directory, JsonSerializer())

    def save_all(self, entries: tuple[Entry, ...]) -> None:
        payload = [self._entry_to_dict(e) for e in entries]
        self._storage.save("entries", payload)

    def load_all(self) -> list[Entry]:
        payload = self._storage.load("entries")
        if not payload:
            return []
        return [self._dict_to_entry(d) for d in payload]

    @staticmethod
    def _entry_to_dict(entry: Entry) -> dict:
        return {
            "id": str(entry.id),
            "title": entry.title,
            "content": entry.content,
            "last_modified": entry.last_modified.isoformat(),
            "manual_links": [
                {"target_id": str(l.target_id), "kind": l.kind, "score": l.score}
                for l in entry.manual_links
            ],
        }

    @staticmethod
    def _dict_to_entry(data: dict) -> Entry:
        entry = Entry(
            id=UUID(data["id"]),
            title=data["title"],
            content=data["content"],
            last_modified=datetime.fromisoformat(data["last_modified"]),
        )
        entry.manual_links = [
            Link(target_id=UUID(l["target_id"]), kind=l["kind"], score=l.get("score", 0.0))
            for l in data.get("manual_links", [])
        ]
        return entry
