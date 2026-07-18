//! KIVO Engine (Rust-Port)
//!
//! Diese Datei verdrahtet die einzelnen Module.
//! Phase 1: Datenmodell, Persistenz, Tokenizer/Stopwords/Normalizer.
//! Phase 2: Fuzzy-Matching, Synonyme, Text-Cleaning, Repository, SearchStage.
//! Phase 3: Analysis/Discovery (Self-Discovery-Konzepte), Learning
//!          (Behavior-Bonus), KeywordExtractor/Scorer/ResultBuilder.
//! Graph/Link-Suggester und die KnowledgeEngine-Fassade (aequivalent zu
//! search/engine.py) kommen in Phase 4-5 dazu.

pub mod analysis;
pub mod discovery;
pub mod entry;
pub mod learning;
pub mod pipeline;
pub mod repository;
pub mod store;
pub mod synonyms;
pub mod text_cleaning;
