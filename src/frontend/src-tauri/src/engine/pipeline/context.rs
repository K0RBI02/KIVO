//! KIVO Search Engine (Rust-Port)
//! Pipeline Context
//!
//! 1:1-Port von `src/engine/search/pipeline/context.py`.
//!
//! WICHTIGE KORREKTUR gegenueber Phase 2: `candidates` nutzt jetzt
//! `IndexMap` statt `HashMap`. Grund: Python-Dicts sind seit 3.7
//! insertion-ordered, und `ResultBuilder` verlaesst sich darauf indirekt -
//! Python's `list.sort()` ist stabil, das heisst bei GLEICHEM Score
//! entscheidet die Original-Reihenfolge (= Einfuegereihenfolge in
//! `candidates`) ueber die Endreihenfolge. Ein `std::collections::HashMap`
//! hat dagegen KEINE garantierte Iterationsreihenfolge - bei Score-
//! Gleichstand koennte die Sortierung dann von Lauf zu Lauf leicht anders
//! ausfallen als im Original. `IndexMap` bewahrt die Einfuegereihenfolge
//! (wie ein Python-Dict) und macht `Vec::sort_by` (ebenfalls dokumentiert
//! stabil) damit 1:1 deterministisch zum Original.

use std::collections::HashMap;
use indexmap::IndexMap;
use uuid::Uuid;

use crate::engine::entry::Entry;

#[derive(Debug, Clone)]
pub struct Candidate {
    pub entry: Entry,
    pub title_hits: usize,
    pub content_hits: usize,
    pub prefix_hits: Vec<String>,
    pub synonym_hits: Vec<(String, String)>,
    pub fuzzy_hits: Vec<(String, String, f64)>,
    pub phrase_match: bool,
}

/// Entspricht `SearchResult` aus result_builder.py.
#[derive(Debug, Clone)]
pub struct SearchResult {
    pub entry: Entry,
    pub score: f64,
}

#[derive(Debug, Clone, Default)]
pub struct PipelineContext {
    pub raw_query: String,
    pub tokens: Vec<String>,
    pub filtered_tokens: Vec<String>,
    pub normalized_tokens: Vec<String>,
    pub weighted_tokens: HashMap<String, f64>,
    pub candidates: IndexMap<Uuid, Candidate>,
    pub scores: HashMap<Uuid, f64>,
    pub results: Vec<SearchResult>,
}

impl PipelineContext {
    pub fn new(raw_query: String) -> Self {
        Self {
            raw_query,
            ..Default::default()
        }
    }
}
