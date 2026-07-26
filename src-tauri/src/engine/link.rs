//! KIVO Search Engine (Rust-Port)
//! Link
//!
//! 1:1-Port von `src/engine/search/link.py`.
//!
//! STRUKTUR-HINWEIS: `Link`/`LinkKind` selbst liegen bei diesem Port
//! bereits seit Phase 1 in `entry.rs` (weil `Entry` sie direkt braucht) -
//! im Python-Original ist das getrennt (`entry.py` importiert aus
//! `link.py`). Rein strukturelle Abweichung, keine Verhaltensaenderung.
//! Diese Datei enthaelt nur die eigentliche Kombinier-Logik.
//!
//! Regel aus dem Original: 0 manuelle -> 3 Vorschlaege, 1 manuelle -> 1
//! manuell + 2 Vorschlaege, 2 manuelle -> 2 manuell + 1 Vorschlag, 3+
//! manuelle -> nur die manuellen, 0 Vorschlaege. Manuelle Links kommen
//! immer zuerst.

use std::cmp::Ordering;
use std::collections::HashSet;
use uuid::Uuid;

use crate::engine::entry::Link;

/// Entspricht `combine_links(manual, suggested, max_total)`.
pub fn combine_links(manual: &[Link], suggested: &[Link], max_total: usize) -> Vec<Link> {
    let manual: Vec<Link> = manual.iter().take(max_total).cloned().collect();
    let remaining_slots = max_total.saturating_sub(manual.len());

    let manual_targets: HashSet<Uuid> = manual.iter().map(|l| l.target_id).collect();

    let mut ranked_suggestions: Vec<Link> = suggested
        .iter()
        .filter(|s| !manual_targets.contains(&s.target_id))
        .cloned()
        .collect();

    // Python: `sorted(..., key=lambda s: s.score, reverse=True)` (stabil).
    ranked_suggestions.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(Ordering::Equal));

    let mut result = manual;
    result.extend(ranked_suggestions.into_iter().take(remaining_slots));
    result
}
