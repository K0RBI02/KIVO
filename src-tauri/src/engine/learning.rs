//! KIVO Search Engine (Rust-Port)
//! Learning (Benutzerverhalten)
//!
//! 1:1-Port von `src/engine/search/learning.py`.
//! "Benutzerverhalten darf niemals einen besseren Treffer ueberholen" -
//! deshalb ist der Bonus hier hart gedeckelt (MAX_BEHAVIOR_BONUS), siehe
//! Docstring im Original.

use std::collections::HashMap;
use uuid::Uuid;

pub const MAX_BEHAVIOR_BONUS: f64 = 0.3;

#[derive(Debug, Default)]
pub struct BehaviorMemory {
    // (normalisierter query-text) -> {entry_id: mal_ausgewaehlt}
    selections: HashMap<String, HashMap<Uuid, u64>>,
}

impl BehaviorMemory {
    pub fn new() -> Self {
        Self::default()
    }

    /// Entspricht `BehaviorMemory.record_selection(query, entry_id)`.
    pub fn record_selection(&mut self, query: &str, entry_id: Uuid) {
        let key = query.trim().to_lowercase();
        *self
            .selections
            .entry(key)
            .or_default()
            .entry(entry_id)
            .or_insert(0) += 1;
    }

    /// Entspricht `BehaviorMemory.bonus_for(query, entry_id)`.
    pub fn bonus_for(&self, query: &str, entry_id: Uuid) -> f64 {
        let key = query.trim().to_lowercase();
        let counts = match self.selections.get(&key) {
            Some(c) => c,
            None => return 0.0,
        };

        let total: u64 = counts.values().sum();
        if total == 0 {
            return 0.0;
        }

        let this_entry = *counts.get(&entry_id).unwrap_or(&0);
        (this_entry as f64 / total as f64) * MAX_BEHAVIOR_BONUS
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unknown_query_has_zero_bonus() {
        let memory = BehaviorMemory::new();
        assert_eq!(memory.bonus_for("nie gesehen", Uuid::new_v4()), 0.0);
    }

    #[test]
    fn always_selected_entry_gets_full_capped_bonus() {
        let mut memory = BehaviorMemory::new();
        let id = Uuid::new_v4();
        memory.record_selection("docker", id);
        memory.record_selection("docker", id);
        // 2 von 2 Auswahlen -> ratio 1.0 -> voller Bonus
        assert!((memory.bonus_for("docker", id) - MAX_BEHAVIOR_BONUS).abs() < 1e-12);
    }
}
