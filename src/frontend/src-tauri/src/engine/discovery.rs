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
//! SCOPE-HINWEIS: das Python-Original erlaubt optionale `stopwords`/
//! `normalizer`-Parameter fuer Sprachumschaltung (language.py, snowball-
//! Stemmer). Dieser Rust-Port deckt bisher nur den Default-Modus ab
//! (kombinierte DE+EN-Stopwords + heuristischer Normalizer) - das ist
//! exakt das Verhalten, das KIVO bisher mit `language="auto"` (dem
//! Standard) sowieso genutzt hat. Eine echte Sprachumschaltung waere ein
//! separater, spaeterer Ausbauschritt, falls gewuenscht.

use std::collections::HashSet;

use crate::engine::analysis::{Analysis, ConceptStats};
use crate::engine::entry::Entry;
use crate::engine::pipeline::normalizer;
use crate::engine::pipeline::stopwords::all_stopwords;
use crate::engine::pipeline::tokenizer;
use crate::engine::text_cleaning::strip_media;

/// Entspricht `discover(entries)` (Default-Modus, siehe Scope-Hinweis oben).
pub fn discover(entries: &[Entry]) -> Analysis {
    let stopwords = all_stopwords();

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
