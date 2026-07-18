//! KIVO Engine (Rust-Port)
//!
//! Diese Datei verdrahtet die einzelnen Module. Phase 1 enthaelt das
//! Datenmodell, die Persistenz und die ersten Pipeline-Stufen
//! (Tokenizer, Stopwords, Normalizer). Scorer, Discovery, Graph,
//! Learning etc. kommen in den naechsten Phasen dazu - bis dahin ist
//! `KnowledgeEngine` (die Fassade, aequivalent zu search/engine.py)
//! noch nicht Teil dieses Moduls.

pub mod entry;
pub mod pipeline;
pub mod store;
