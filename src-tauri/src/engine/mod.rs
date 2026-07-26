//! KIVO Engine (Rust-Port)
//!
//! Diese Datei verdrahtet die einzelnen Module.
//! Phase 1: Datenmodell, Persistenz, Tokenizer/Stopwords/Normalizer.
//! Phase 2: Fuzzy-Matching, Synonyme, Text-Cleaning, Repository, SearchStage.
//! Phase 3: Analysis/Discovery, Learning (Behavior-Bonus),
//!          KeywordExtractor/Scorer/ResultBuilder.
//! Phase 4: Link-Kombinierung + Link-Suggester.
//! Phase 5: `engine`-Submodul = die KnowledgeEngine-Fassade (aequivalent
//!          zu Python's search/engine.py), verbindet alles zu einer
//!          einzigen Anlaufstelle fuer die Tauri-Commands.
//!
//! NAMENS-HINWEIS: dieses Modul (der Ordner `engine/`) entspricht in etwa
//! Python's `search`-Subpackage; das darin liegende `engine.rs` entspricht
//! Python's `search/engine.py`. Der Pfad `crate::engine::engine::
//! KnowledgeEngine` sieht dadurch etwas redundant aus - funktional korrekt,
//! aber falls das stoert, liesse sich der aeussere Ordner jederzeit
//! risikolos umbenennen (reine Kosmetik, keine Verhaltensaenderung).

pub mod analysis;
pub mod discovery;
pub mod engine;
pub mod entry;
pub mod learning;
pub mod link;
pub mod link_suggester;
pub mod pipeline;
pub mod repository;
pub mod store;
pub mod synonyms;
pub mod text_cleaning;
