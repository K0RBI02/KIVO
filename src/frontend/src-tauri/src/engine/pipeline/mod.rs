//! KIVO Search Engine (Rust-Port)
//! Pipeline-Module.
//! Phase 1: Tokenizer, Stopwords, Normalizer.
//! Phase 2: Context, Fuzzy-Matching, SearchStage.
//! Phase 3: KeywordExtractor, Scorer, ResultBuilder.
//! (Discovery/Analysis liegen wie im Python-Original NICHT unter pipeline/,
//! sondern eine Ebene hoeher unter engine/ - siehe engine/mod.rs)

pub mod context;
pub mod fuzzy;
pub mod keyword_extractor;
pub mod normalizer;
pub mod result_builder;
pub mod scorer;
pub mod search_stage;
pub mod stopwords;
pub mod tokenizer;
