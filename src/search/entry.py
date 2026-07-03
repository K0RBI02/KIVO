"""
KIVO Search Engine
Entry - das einzige Nutzer-Datenmodell.

Bewusst minimal (siehe Spec): ID, Titel, Inhalt, LastModified, Links.
Keine weiteren Pflichtfelder. Kein Pfad, kein Ordner, keine Hierarchie.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .link import Link


@dataclass(slots=True)
class Entry:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Nur MANUELLE Links gehoeren zum Entry selbst (Nutzerdaten).
    # Automatische Vorschlaege werden zur Laufzeit von der Engine berechnet,
    # NICHT gespeichert -> strikte Trennung Nutzerdaten / Engine-Daten.
    manual_links: list[Link] = field(default_factory=list)

    def touch(self) -> None:
        self.last_modified = datetime.now(timezone.utc)

    def add_manual_link(self, target_id: UUID) -> None:
        if any(l.target_id == target_id for l in self.manual_links):
            return
        self.manual_links.append(Link(target_id=target_id, kind="manual"))
        self.touch()

    def remove_manual_link(self, target_id: UUID) -> None:
        self.manual_links = [l for l in self.manual_links if l.target_id != target_id]
        self.touch()
