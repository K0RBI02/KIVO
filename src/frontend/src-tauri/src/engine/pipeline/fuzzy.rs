//! KIVO Search Engine (Rust-Port)
//! Fuzzy Matching
//!
//! 1:1-Port von `src/engine/search/pipeline/fuzzy.py`.
//!
//! Python nutzt `difflib.SequenceMatcher(None, a, b).ratio()` (Ratcliff/
//! Obershelp-Algorithmus). Es gibt keine bit-identische Rust-Bibliothek
//! dafuer (andere Crates wie strsim nutzen andere Algorithmen wie Jaro-
//! Winkler oder Levenshtein - das waeren KEINE 1:1-Ports, sondern andere
//! Formeln mit anderen Ergebnissen). Deshalb ist der Kern-Algorithmus hier
//! von Hand nachgebaut.
//!
//! WICHTIG - Scope-Einschraenkung (bewusst, siehe Docstring in fuzzy.py):
//! difflib's "autojunk"-Heuristik greift nur bei Sequenzen ab 200 Zeichen
//! Laenge. Da hier ausschliesslich einzelne, normalisierte Wort-Tokens
//! verglichen werden (nie ganze Dokumente), kommt Autojunk in der Praxis
//! nie zum Tragen - der Kern-Algorithmus ohne Junk-Handling ist fuer diesen
//! Anwendungsfall exakt aequivalent. Vor dem Rust-Port wurde diese
//! Nachimplementierung gegen das echte `difflib` mit 509 Wortpaaren
//! (kuratiert + zufaellig) verifiziert: 0 Abweichungen.

use std::collections::HashMap;

pub const DEFAULT_THRESHOLD: f64 = 0.72;
const MIN_LENGTH_FOR_FUZZY: usize = 4;

/// Findet den laengsten zusammenhaengenden uebereinstimmenden Block
/// zwischen a[alo..ahi] und b[blo..bhi]. 1:1-Port von difflib's
/// `find_longest_match` (ohne Junk-Handling, siehe Modul-Doku).
fn find_longest_match(
    a: &[char],
    b: &[char],
    b2j: &HashMap<char, Vec<usize>>,
    alo: usize,
    ahi: usize,
    blo: usize,
    bhi: usize,
) -> (usize, usize, usize) {
    let mut best_i = alo;
    let mut best_j = blo;
    let mut best_size = 0usize;
    let mut j2len: HashMap<usize, usize> = HashMap::new();

    for i in alo..ahi {
        let mut newj2len: HashMap<usize, usize> = HashMap::new();
        if let Some(js) = b2j.get(&a[i]) {
            for &j in js {
                if j < blo {
                    continue;
                }
                if j >= bhi {
                    break;
                }
                let prev = if j == 0 { 0 } else { *j2len.get(&(j - 1)).unwrap_or(&0) };
                let k = prev + 1;
                newj2len.insert(j, k);
                if k > best_size {
                    best_i = i + 1 - k;
                    best_j = j + 1 - k;
                    best_size = k;
                }
            }
        }
        j2len = newj2len;
    }

    (best_i, best_j, best_size)
}

/// 1:1-Port von difflib's `get_matching_blocks` (Kern-Rekursion, ohne die
/// abschliessende Merge-/Junk-Nachbereitung - fuer die reine Summe der
/// Match-Groessen in `ratio()` macht das keinen Unterschied, siehe Modul-Doku).
fn get_matching_blocks(a: &[char], b: &[char]) -> Vec<(usize, usize, usize)> {
    let mut b2j: HashMap<char, Vec<usize>> = HashMap::new();
    for (idx, &ch) in b.iter().enumerate() {
        b2j.entry(ch).or_default().push(idx);
    }

    let mut queue = vec![(0usize, a.len(), 0usize, b.len())];
    let mut blocks = Vec::new();

    while let Some((alo, ahi, blo, bhi)) = queue.pop() {
        let (i, j, k) = find_longest_match(a, b, &b2j, alo, ahi, blo, bhi);
        if k > 0 {
            blocks.push((i, j, k));
            if alo < i && blo < j {
                queue.push((alo, i, blo, j));
            }
            if i + k < ahi && j + k < bhi {
                queue.push((i + k, ahi, j + k, bhi));
            }
        }
    }

    blocks
}

/// Entspricht `SequenceMatcher(None, a, b).ratio()`.
pub fn similarity(a: &str, b: &str) -> f64 {
    let a_chars: Vec<char> = a.chars().collect();
    let b_chars: Vec<char> = b.chars().collect();

    let blocks = get_matching_blocks(&a_chars, &b_chars);
    let matches: usize = blocks.iter().map(|&(_, _, k)| k).sum();
    let total = a_chars.len() + b_chars.len();

    if total == 0 {
        return 1.0;
    }
    2.0 * matches as f64 / total as f64
}

/// Entspricht `best_fuzzy_match(token, candidates, threshold)`.
/// Gibt `Some((bestes_wort, score))` zurueck, oder `None` wenn nichts ueber
/// dem Schwellwert liegt (bzw. `token` zu kurz fuer Fuzzy-Matching ist).
pub fn best_fuzzy_match(
    token: &str,
    candidates: &[String],
    threshold: f64,
) -> Option<(String, f64)> {
    if token.chars().count() < MIN_LENGTH_FOR_FUZZY {
        return None;
    }

    let mut best_word: Option<String> = None;
    let mut best_score = 0.0f64;

    for candidate in candidates {
        if candidate.chars().count() < MIN_LENGTH_FOR_FUZZY {
            continue;
        }
        let score = similarity(token, candidate);
        if score > best_score {
            best_score = score;
            best_word = Some(candidate.clone());
        }
    }

    match best_word {
        Some(word) if best_score >= threshold => Some((word, best_score)),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // Erwartungswerte 1:1 aus dem echten Python difflib.SequenceMatcher
    // uebernommen (siehe Verifikations-Skript in der Konversation).
    #[test]
    fn matches_python_difflib_ratio_exactly() {
        let cases: &[(&str, &str, f64)] = &[
            ("proxy", "proxydings", 0.6666666666666666),
            ("proxy-dings", "proxy", 0.625),
            ("caddy", "caddi", 0.8),
            ("fedora", "fedroa", 0.8333333333333334),
            ("docker", "dockerr", 0.9230769230769231),
            ("installieren", "instalieren", 0.9565217391304348),
            ("konfiguration", "konfig", 0.631578947368421),
            ("systemctl", "systemct", 0.9411764705882353),
            ("linux", "linus", 0.8),
        ];
        for (a, b, expected) in cases {
            let got = similarity(a, b);
            assert!(
                (got - expected).abs() < 1e-9,
                "similarity({a:?}, {b:?}) = {got}, erwartet {expected}"
            );
        }
    }

    #[test]
    fn respects_threshold_and_min_length() {
        let candidates = vec!["proxy".to_string(), "docker".to_string()];
        // "pro" ist zu kurz (< 4 Zeichen) -> kein Fuzzy-Match
        assert_eq!(best_fuzzy_match("pro", &candidates, DEFAULT_THRESHOLD), None);
        // "proxi" ist nah genug an "proxy"
        assert!(best_fuzzy_match("proxi", &candidates, DEFAULT_THRESHOLD).is_some());
    }
}
