//! KIVO Search Engine (Rust-Port)
//! Link Suggester
//!
//! 1:1-Port von `src/engine/search/link_suggester.py`.
//! Berechnet automatische Link-Vorschlaege ueber gemeinsame entdeckte
//! Konzepte zwischen Entry-Paaren, kombiniert mit manuellen Links nach der
//! Regel aus link.rs (max 3, manuelle zuerst).
//!
//! SCOPE-ENTSCHEIDUNG (bitte bei Bedarf Bescheid geben): das Python-
//! Original nimmt einen `graph: KnowledgeGraph`-Parameter entgegen, liest
//! ihn aber im gesamten Funktionskoerper nie - verifiziert per grep gegen
//! den echten Quellcode (siehe Konversation). Die generische Knowledge-
//! Graph/Domain-Maschinerie (Node/Relation/DomainManager/EventBus) wird
//! ausserdem von keiner aktiven API-Route genutzt (`engine.related_
//! concepts()` ist in `webapp/server.py` nicht als Endpunkt exposed).
//! Diese Datei portiert deshalb bewusst nur den tatsaechlich wirksamen
//! Teil (direkter Konzept-Abgleich zwischen Entry-Paaren) - kein toter
//! Code wird mitgeschleppt. Falls fuer geplante Zukunftsfeatures doch der
//! volle Graph gebraucht wird, ist das ein eigener, klar abgrenzbarer
//! Nachtrag.

use std::collections::HashSet;

use crate::engine::analysis::Analysis;
use crate::engine::entry::{Entry, Link, LinkKind};
use crate::engine::link::combine_links;
use crate::engine::pipeline::normalizer;
use crate::engine::pipeline::tokenizer;
use crate::engine::text_cleaning::strip_media;

/// Entspricht `suggest_links(entry, all_entries, analysis, graph, max_total,
/// stopwords)` (ohne den ungenutzten `graph`-Parameter, siehe Modul-Doku).
pub fn suggest_links(
    entry: &Entry,
    all_entries: &[Entry],
    analysis: &Analysis,
    max_total: usize,
    stopwords: &HashSet<&'static str>,
) -> Vec<Link> {
    let text = strip_media(&format!("{} {}", entry.title, entry.content));
    let concept_terms: HashSet<String> = tokenizer::tokenize(&text)
        .into_iter()
        .filter(|t| !stopwords.contains(t.as_str()))
        .map(|t| normalizer::normalize(&t))
        .filter(|t| analysis.is_known_concept(t))
        .collect();

    // Vec statt HashMap, damit die Einfuegereihenfolge (= Reihenfolge von
    // `all_entries`) erhalten bleibt - wichtig fuer stabile Tie-Breaks in
    // combine_links(), genau wie beim insertion-ordered Python-Dict.
    let mut suggested: Vec<Link> = Vec::new();

    for other in all_entries {
        if other.id == entry.id {
            continue;
        }

        let other_text = strip_media(&format!("{} {}", other.title, other.content));
        let other_terms: HashSet<String> = tokenizer::tokenize(&other_text)
            .into_iter()
            .filter(|t| !stopwords.contains(t.as_str()))
            .map(|t| normalizer::normalize(&t))
            .collect();

        let shared_count = concept_terms.intersection(&other_terms).count();
        if shared_count > 0 {
            suggested.push(Link {
                target_id: other.id,
                kind: LinkKind::Suggested,
                score: shared_count as f64,
            });
        }
    }

    combine_links(&entry.manual_links, &suggested, max_total)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::discovery::discover;
    use crate::engine::pipeline::stopwords::all_stopwords;
    use uuid::Uuid;

    fn mkid(n: u128) -> Uuid {
        Uuid::from_u128(n)
    }

    fn build_entries() -> Vec<Entry> {
        vec![
            {
                let mut e = Entry::new(
                    "Caddy Installation".to_string(),
                    "Caddy auf Fedora installieren. Reverse Proxy konfigurieren mit Caddy."
                        .to_string(),
                );
                e.id = mkid(1);
                e
            },
            {
                let mut e = Entry::new(
                    "Docker Commands".to_string(),
                    "Wichtige Docker Befehle: docker compose. Docker fuer Multi-Container Setups."
                        .to_string(),
                );
                e.id = mkid(2);
                e
            },
            {
                let mut e = Entry::new(
                    "Fedora Befehle".to_string(),
                    "Fedora nutzt dnf statt apt. dnf install, dnf update.".to_string(),
                );
                e.id = mkid(3);
                e
            },
            {
                let mut e = Entry::new(
                    "Proxy Konfigurationen".to_string(),
                    "Reverse Proxy Konfiguration mit Caddy oder Nginx. Automatisches HTTPS."
                        .to_string(),
                );
                e.id = mkid(4);
                e
            },
            {
                let mut e = Entry::new(
                    "Linux Tricks".to_string(),
                    "Nuetzliche Linux Kommandos: grep, awk, sed.".to_string(),
                );
                e.id = mkid(5);
                e
            },
        ]
    }

    // Ground-Truth 1:1 aus einem echten Lauf von link_suggester.py
    // uebernommen (siehe Konversation).

    #[test]
    fn suggests_ranked_links_when_no_manual_links_exist() {
        let entries = build_entries();
        let analysis = discover(&entries, &all_stopwords());
        let e1 = &entries[0];

        let result = suggest_links(e1, &entries, &analysis, 3, &all_stopwords());

        assert_eq!(result.len(), 2);
        assert_eq!(result[0].target_id, mkid(4));
        assert_eq!(result[0].kind, LinkKind::Suggested);
        assert!((result[0].score - 4.0).abs() < 1e-9);
        assert_eq!(result[1].target_id, mkid(3));
        assert!((result[1].score - 2.0).abs() < 1e-9);
    }

    #[test]
    fn manual_link_always_comes_first_and_fills_a_slot() {
        let entries = build_entries();
        let analysis = discover(&entries, &all_stopwords());
        let mut e1 = entries[0].clone();
        e1.manual_links.push(Link {
            target_id: mkid(5),
            kind: LinkKind::Manual,
            score: 0.0,
        });

        let result = suggest_links(&e1, &entries, &analysis, 3, &all_stopwords());

        assert_eq!(result.len(), 3);
        assert_eq!(result[0].target_id, mkid(5));
        assert_eq!(result[0].kind, LinkKind::Manual);
        assert_eq!(result[1].target_id, mkid(4));
        assert_eq!(result[2].target_id, mkid(3));
    }

    #[test]
    fn three_manual_links_leave_no_room_for_suggestions() {
        let entries = build_entries();
        let analysis = discover(&entries, &all_stopwords());
        let mut e1 = entries[0].clone();
        for n in [2u128, 3, 4] {
            e1.manual_links.push(Link {
                target_id: mkid(n),
                kind: LinkKind::Manual,
                score: 0.0,
            });
        }

        let result = suggest_links(&e1, &entries, &analysis, 3, &all_stopwords());

        assert_eq!(result.len(), 3);
        assert!(result.iter().all(|l| l.kind == LinkKind::Manual));
    }
}
