"""
KIVO Search Engine
Synonyms

Bewusst als austauschbares Modul (Datei), nicht hart im Code -
kann spaeter pro Sprache ersetzt oder vom Nutzer erweitert werden,
ohne dass die Pipeline angefasst wird.

WICHTIG laut Scorer-Prioritaet: Synonyme rangieren UNTER Titel/Inhalt/
Fuzzy - sie oeffnen nur zusaetzliche Kandidaten, ueberholen aber nie
einen direkten Treffer.
"""

from __future__ import annotations

from pathlib import Path
import json

_DEFAULT_GROUPS: list[list[str]] = [
    ["proxy", "reverseproxy", "revers"],
    ["install", "setup", "einrichtung", "einrichten"],
    ["config", "konfig", "konfiguration", "settings"],
    ["docker", "container"],
    ["fedora", "linux", "dnf"],
    ["network", "netzwerk", "netz"],
    ["service", "dienst", "systemctl"],
    ["https", "ssl", "tls", "zertifikat"],
]


class SynonymDictionary:

    def __init__(self, groups: list[list[str]] | None = None) -> None:
        self._term_to_group: dict[str, set[str]] = {}
        self._load(groups if groups is not None else _DEFAULT_GROUPS)

    def _load(self, groups: list[list[str]]) -> None:
        # WICHTIG: dieselbe Normalisierung wie die Suche verwenden,
        # sonst passen z.B. "einrichten" (Dictionary) und "einricht"
        # (normalisierter Suchbegriff) nie zusammen.
        from .pipeline.normalizer import Normalizer
        normalizer = Normalizer()

        for group in groups:
            normalized_group = {normalizer.normalize(term) for term in group}
            for term in normalized_group:
                self._term_to_group.setdefault(term, set()).update(normalized_group)

    def expand(self, term: str) -> set[str]:
        """Alle bekannten Synonyme eines Begriffs (inkl. dem Begriff selbst)."""
        return self._term_to_group.get(term, {term})

    @classmethod
    def from_file(cls, path: str | Path) -> "SynonymDictionary":
        """Laedt zusaetzliche/eigene Synonymgruppen aus einer JSON-Datei."""
        p = Path(path)
        if not p.exists():
            return cls()
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(groups=data.get("groups", []))
