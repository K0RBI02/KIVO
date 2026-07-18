//! KIVO Search Engine (Rust-Port)
//! Synonyms
//!
//! 1:1-Port von `src/engine/search/synonyms.py`.
//! Bewusst als austauschbare Wortgruppen-Liste (nicht hart im Code) - wie
//! im Original als Datenstruktur gehalten, damit sie spaeter leicht
//! erweiterbar bleibt.
//!
//! WICHTIG: die Gruppenbegriffe werden beim Laden durch den Normalizer aus
//! Phase 1 geschickt (identisch zum Python-Original), damit z.B. "einrichten"
//! (Woerterbuch) und "einricht" (normalisierter Suchbegriff) zusammenfinden.

use std::collections::{HashMap, HashSet};

use crate::engine::pipeline::normalizer;

pub const DEFAULT_GROUPS: &[&[&str]] = &[
    &["proxy", "reverseproxy", "revers"],
    &["install", "setup", "einrichtung", "einrichten"],
    &["config", "konfig", "konfiguration", "settings"],
    &["docker", "container"],
    &["fedora", "linux", "dnf"],
    &["network", "netzwerk", "netz"],
    &["service", "dienst", "systemctl"],
    &["https", "ssl", "tls", "zertifikat"],
];

pub struct SynonymDictionary {
    term_to_group: HashMap<String, HashSet<String>>,
}

impl SynonymDictionary {
    /// Entspricht `SynonymDictionary()` (nutzt `_DEFAULT_GROUPS`).
    pub fn new() -> Self {
        let groups: Vec<Vec<String>> = DEFAULT_GROUPS
            .iter()
            .map(|group| group.iter().map(|s| s.to_string()).collect())
            .collect();
        Self::with_groups(&groups)
    }

    /// Entspricht `SynonymDictionary(groups=...)` / `_load()`.
    pub fn with_groups(groups: &[Vec<String>]) -> Self {
        let mut term_to_group: HashMap<String, HashSet<String>> = HashMap::new();

        for group in groups {
            let normalized_group: HashSet<String> =
                group.iter().map(|term| normalizer::normalize(term)).collect();

            for term in &normalized_group {
                term_to_group
                    .entry(term.clone())
                    .or_default()
                    .extend(normalized_group.iter().cloned());
            }
        }

        Self { term_to_group }
    }

    /// Entspricht `SynonymDictionary.expand(term)`: alle bekannten Synonyme
    /// eines Begriffs (inkl. dem Begriff selbst), oder nur der Begriff
    /// selbst, falls er in keiner Gruppe vorkommt.
    pub fn expand(&self, term: &str) -> HashSet<String> {
        match self.term_to_group.get(term) {
            Some(set) => set.clone(),
            None => {
                let mut s = HashSet::new();
                s.insert(term.to_string());
                s
            }
        }
    }
}

impl Default for SynonymDictionary {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_known_group_both_directions() {
        let dict = SynonymDictionary::new();
        let expanded = dict.expand(&normalizer::normalize("proxy"));
        assert!(expanded.contains(&normalizer::normalize("reverseproxy")));
        assert!(expanded.contains(&normalizer::normalize("revers")));
    }

    #[test]
    fn unknown_term_expands_to_itself_only() {
        let dict = SynonymDictionary::new();
        let expanded = dict.expand("voellig_unbekannt");
        assert_eq!(expanded.len(), 1);
        assert!(expanded.contains("voellig_unbekannt"));
    }
}
