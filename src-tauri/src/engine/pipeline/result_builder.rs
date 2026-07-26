//! KIVO Search Engine (Rust-Port)
//! Result Builder
//!
//! 1:1-Port von `src/engine/search/pipeline/result_builder.py`.
//! Aufgabe: aus den Scores fertige SearchResults bauen, sortiert.
//!
//! WICHTIG: verlaesst sich auf `context.candidates` als insertion-ordered
//! Map (siehe Korrektur-Hinweis in context.rs) UND auf `Vec::sort_by` als
//! stabilen Sort (dokumentiertes Verhalten von Rust's Standardbibliothek) -
//! zusammen ergibt das dieselbe Tie-Break-Reihenfolge bei Score-Gleichstand
//! wie Python's `list.sort()` (ebenfalls stabil) auf einem insertion-
//! ordered Dict.

use crate::engine::pipeline::context::{PipelineContext, SearchResult};

pub struct ResultBuilder;

impl ResultBuilder {
    /// Entspricht `ResultBuilder.execute(context)`.
    pub fn execute(context: &mut PipelineContext) {
        let mut results: Vec<SearchResult> = context
            .candidates
            .iter()
            .map(|(entry_id, candidate)| {
                let score = context.scores.get(entry_id).copied().unwrap_or(0.0);
                SearchResult {
                    entry: candidate.entry.clone(),
                    score,
                }
            })
            .collect();

        // Python: `results.sort(key=lambda r: r.score, reverse=True)`
        // (stabil). `sort_by` in Rust ist ebenfalls stabil - siehe
        // Modul-Doku oben.
        results.sort_by(|a, b| {
            b.score
                .partial_cmp(&a.score)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        context.results = results.into_iter().filter(|r| r.score > 0.0).collect();
    }
}
