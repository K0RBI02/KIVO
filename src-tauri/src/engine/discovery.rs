//! KIVO Search Engine (Rust-Port)
//! Discovery
//!
//! 1:1-Port von `src/engine/search/discovery.py`.
//!
//! Die groesste Architekturentscheidung aus der Python-Spec bleibt
//! erhalten: die Engine besitzt KEIN eingebautes Weltwissen. Sie
//! beobachtet, welche Begriffe in mehreren Entries auftauchen, und
//! erklaert die selbst zu "Konzepten".
//!
//! SPRACH-HINWEIS: `stopwords` ist jetzt parametrisiert (siehe
//! `pipeline::stopwords::stopwords_for`) - die Sprachumschaltung "auto"/
//! "de"/"en" wirkt sich also auf die Stopword-Filterung aus. Der
//! Normalizer bleibt weiterhin immer der heuristische (kein Snowball-
//! Stemmer-Support) - siehe Scope-Hinweis in `pipeline::stopwords`.

use std::collections::HashSet;

use crate::engine::analysis::{Analysis, ConceptStats};
use crate::engine::entry::Entry;
use crate::engine::pipeline::normalizer;
use crate::engine::pipeline::tokenizer;
use crate::engine::text_cleaning::strip_media;

/// Entspricht `discover(entries, stopwords=...)`. `stopwords` steuert die
/// Sprachumschaltung (siehe `pipeline::stopwords::stopwords_for`).
pub fn discover(entries: &[Entry], stopwords: &HashSet<&'static str>) -> Analysis {
    let mut analysis = Analysis::new();
    analysis.total_documents = entries.len();

    for entry in entries {
        let text = strip_media(&format!("{} {}", entry.title, entry.content));
        let raw_tokens = tokenizer::tokenize(&text);
        let filtered: Vec<String> = raw_tokens
            .into_iter()
            .filter(|t| !stopwords.contains(t.as_str()))
            .collect();
        let normalized: Vec<String> = filtered.iter().map(|t| normalizer::normalize(t)).collect();

        let mut seen_in_this_entry: HashSet<String> = HashSet::new();

        for term in normalized {
            if term.chars().count() < 2 {
                continue;
            }

            let stats = analysis
                .concepts
                .entry(term.clone())
                .or_insert_with(|| ConceptStats::new(term.clone()));
            stats.total_frequency += 1;

            if !seen_in_this_entry.contains(&term) {
                stats.document_frequency += 1;
                stats.entry_ids.insert(entry.id);
                seen_in_this_entry.insert(term);
            }
        }
    }

    analysis
}
