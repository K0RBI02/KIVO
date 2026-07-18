//! KIVO Search Engine (Rust-Port)
//! Entry Repository
//!
//! 1:1-Port von `src/engine/search/repository.py`.
//! Reine In-Memory-Verwaltung. Kein Ranking, kein Scoring, keine
//! Business-Logik.
//!
//! KORREKTUR (Phase 3, siehe context.rs): nutzt jetzt `IndexMap` statt
//! `HashMap`, damit `get_all()` die Entries in Einfuegereihenfolge liefert -
//! exakt wie Python's insertion-ordered Dict. Das ist Voraussetzung dafuer,
//! dass SearchStage/ResultBuilder bei Score-Gleichstand dieselbe
//! Tie-Break-Reihenfolge liefern wie das Original.

use indexmap::IndexMap;
use uuid::Uuid;

use crate::engine::entry::Entry;

pub struct EntryRepository {
    entries: IndexMap<Uuid, Entry>,
}

impl EntryRepository {
    pub fn new() -> Self {
        Self {
            entries: IndexMap::new(),
        }
    }

    pub fn create(&mut self, entry: Entry) -> Entry {
        let clone = entry.clone();
        self.entries.insert(entry.id, entry);
        clone
    }

    pub fn update(&mut self, mut entry: Entry) -> Entry {
        entry.touch();
        let clone = entry.clone();
        self.entries.insert(entry.id, entry);
        clone
    }

    pub fn delete(&mut self, entry_id: Uuid) {
        self.entries.shift_remove(&entry_id);
    }

    pub fn get(&self, entry_id: Uuid) -> Option<Entry> {
        self.entries.get(&entry_id).cloned()
    }

    pub fn get_all(&self) -> Vec<Entry> {
        self.entries.values().cloned().collect()
    }

    /// Entspricht der rohen Substring-Suche in repository.py. Wird von der
    /// gerankten Pipeline NICHT verwendet, nur der Vollstaendigkeit halber
    /// mit portiert.
    #[allow(dead_code)]
    pub fn search(&self, term: &str) -> Vec<Entry> {
        let term = term.to_lowercase();
        self.entries
            .values()
            .filter(|e| {
                e.title.to_lowercase().contains(&term) || e.content.to_lowercase().contains(&term)
            })
            .cloned()
            .collect()
    }
}

impl Default for EntryRepository {
    fn default() -> Self {
        Self::new()
    }
}
