# KIVO starten

Zwei Prozesse, zwei Terminals. Kein Docker, kein extra pip-Paket noetig.

Struktur:
```
kivo-final/
  src/
    engine/     <- Python: Suche, Discovery, API-Server
    frontend/   <- React/Vite: dein Design
```

## 1. Engine + API starten

```
cd src/engine
python3 webapp/server.py
```

Laeuft dann auf `http://127.0.0.1:8420`. Laesst du das Fenster offen,
bleiben deine Notizen erhalten (Datei `src/engine/kivo_data/entries.json`).

## 2. Frontend starten (dein Design)

Zweites Terminal:

```
cd src/frontend
npm i
npm run dev
```

Browser oeffnet sich automatisch (oder die von Vite angezeigte URL aufrufen).

## Was du jetzt ausprobieren kannst

- Neue Notiz anlegen (Stift-Icon unten rechts oder ⌘N)
- Nach einem Wort suchen, das NICHT im Titel steht, nur im Inhalt
- Absichtlich unscharf/falsch tippen (Fuzzy Matching)
- Zwei Notizen mit gemeinsamem Begriff anlegen (z.B. "Docker" in beiden),
  eine davon oeffnen -> unten bei "Related" taucht die andere automatisch
  als Vorschlag (ⓘ) auf, ganz ohne manuelles Verlinken
- App komplett schliessen und neu starten -> Notizen sind noch da

## Was noch fehlt / als Naechstes ansteht

- "Export/Import/Delete all data" in den Settings sind noch reine
  Platzhalter-Buttons
- Manuelle Links gibt es engine-seitig (`engine.link(...)` /
  `POST /api/link/<id>`), aber noch keinen UI-Knopf dafuer
- Mehrsprachigkeit (Stopwords/Normalizer) ist vorbereitet, aber nicht
  pro Sprache umschaltbar
