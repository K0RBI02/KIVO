//! KIVO Search Engine (Rust-Port)
//! Tokenizer
//!
//! 1:1-Port von `src/engine/search/pipeline/tokenizer.py`.
//! Aufgabe: Text -> Token[]. Sonst nichts.

use regex::Regex;
use std::sync::OnceLock;

fn token_pattern() -> &'static Regex {
    static PATTERN: OnceLock<Regex> = OnceLock::new();
    PATTERN.get_or_init(|| {
        // Identisch zu Python: r"[a-zA-ZäöüÄÖÜß0-9]+"
        Regex::new(r"[a-zA-Z\u{00e4}\u{00f6}\u{00fc}\u{00c4}\u{00d6}\u{00dc}\u{00df}0-9]+")
            .expect("Token-Regex ist ein festes, gueltiges Muster")
    })
}

/// Entspricht `Tokenizer.tokenize(text)`: Text wird zuerst lowercased
/// (wie Python's `text.lower()`), dann werden alle Treffer des Musters
/// als Tokens zurueckgegeben.
pub fn tokenize(text: &str) -> Vec<String> {
    let lower = text.to_lowercase();
    token_pattern()
        .find_iter(&lower)
        .map(|m| m.as_str().to_string())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_on_non_word_chars_and_lowercases() {
        let tokens = tokenize("Caddy auf Fedora installieren!");
        assert_eq!(tokens, vec!["caddy", "auf", "fedora", "installieren"]);
    }

    #[test]
    fn keeps_german_umlauts_together() {
        let tokens = tokenize("Für Größe über Straße");
        assert_eq!(tokens, vec!["für", "größe", "über", "straße"]);
    }
}
