//! KIVO Search Engine (Rust-Port)
//! Analysis
//!
//! 1:1-Port von `src/engine/search/analysis.py`.
//! Enthaelt ausschliesslich berechnete Daten (Self-Discovery-Ergebnisse).
//! Keine Nutzerdaten - darf jederzeit verworfen und neu berechnet werden.

use std::collections::HashMap;
use std::collections::HashSet;
use uuid::Uuid;

#[derive(Debug, Clone, Default)]
pub struct ConceptStats {
    pub term: String,
    pub document_frequency: u64,
    pub total_frequency: u64,
    pub entry_ids: HashSet<Uuid>,
}

impl ConceptStats {
    pub fn new(term: String) -> Self {
        Self {
            term,
            ..Default::default()
        }
    }

    /// Entspricht der `is_concept`-Property: ein Begriff gilt erst als
    /// "Konzept", wenn er in mindestens 2 Entries auftaucht.
    pub fn is_concept(&self) -> bool {
        self.document_frequency >= 2
    }
}

#[derive(Debug, Default)]
pub struct Analysis {
    pub concepts: HashMap<String, ConceptStats>,
    pub total_documents: usize,
}

impl Analysis {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn is_known_concept(&self, term: &str) -> bool {
        self.concepts.get(term).map(|s| s.is_concept()).unwrap_or(false)
    }

    /// Entspricht `Analysis.concept_weight(term)`. Je seltener/
    /// spezifischer ein entdeckter Begriff, desto staerker sein Gewicht
    /// (idf-artig).
    pub fn concept_weight(&self, term: &str) -> f64 {
        let stats = match self.concepts.get(term) {
            Some(s) => s,
            None => return 1.0,
        };
        if stats.document_frequency == 0 {
            return 1.0;
        }

        let total_docs = self.total_documents.max(1) as f64;
        1.0 + ((total_docs + 1.0) / (stats.document_frequency as f64 + 1.0)).ln()
    }
}
