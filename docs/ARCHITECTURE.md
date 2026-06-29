# Architektur

## Grundprinzip

Clients besitzen keine Geschäftslogik.

Alle Entscheidungen werden ausschließlich von der Engine getroffen.


------------------------------------------------

Desktop
Mobile
CLI
Browser
API

        │
        ▼

Core Engine

        │

├── Query Pipeline
├── Analysis
├── Search
├── Ranking
├── Suggestions
├── Learning
└── Storage

------------------------------------------------


## Query Pipeline

Query

↓

Tokenizer

↓

Stopword Filter

↓

Normalizer

↓

Discovery

↓

Scoring

↓

Results


## Daten

Entry

- ID
- Titel
- Inhalt
- LastModified
- Links


Analysis

- Keywords
- Relations
- Statistics
- Search Metadata
- Learning Data


Die Analysis darf jederzeit neu berechnet werden.

Der Entry bleibt davon unberührt.