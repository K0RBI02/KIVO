"""
KIVO Search Engine
Text Cleaning

Bereinigt Text VOR der Tokenisierung fuer Suche/Discovery/Graph.
Betrifft NUR die Such-Verarbeitung, nicht den gespeicherten Entry-Inhalt
selbst - Bilder bleiben in der Notiz sichtbar, zaehlen nur nicht als
durchsuchbarer "Text".

Grund: eingefuegte Bilder werden als Base64-Data-URI direkt im Markdown
gespeichert (![](data:image/png;base64,....)). Ohne diese Bereinigung
wuerde der Tokenizer den Base64-Blob in hunderte sinnlose "Woerter"
zerlegen - und weil Base64 nur 64 moegliche Zeichen hat, ueberschneiden
sich lange Blobs rein zufaellig zwischen voellig unabhaengigen Bildern.
Das erzeugt falsche "gemeinsame Konzepte" und damit falsche Link-
Vorschlaege.
"""

from __future__ import annotations

import re

# Markdown-Bilder: ![alt](irgendwas) - trifft sowohl data:-URIs als auch
# normale Bild-URLs (auch die sind kein sinnvoller Suchtext).
_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def strip_media(text: str) -> str:
    """Entfernt Markdown-Bilder aus Text, bevor er tokenisiert wird."""
    return _IMAGE_PATTERN.sub(" ", text)
