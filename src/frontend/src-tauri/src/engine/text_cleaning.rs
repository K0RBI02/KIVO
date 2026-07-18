//! KIVO Search Engine (Rust-Port)
//! Text Cleaning
//!
//! 1:1-Port von `src/engine/search/text_cleaning.py`.
//! Entfernt Markdown-Bilder VOR der Tokenisierung fuer Suche/Discovery/
//! Graph (betrifft nur die Such-Verarbeitung, nicht den gespeicherten
//! Entry-Inhalt selbst - siehe ausfuehrliche Begruendung im Python-Original).

use regex::Regex;
use std::sync::OnceLock;

fn image_pattern() -> &'static Regex {
    static PATTERN: OnceLock<Regex> = OnceLock::new();
    PATTERN.get_or_init(|| {
        // Identisch zu Python: r"!\[[^\]]*\]\([^)]*\)"
        Regex::new(r"!\[[^\]]*\]\([^)]*\)").expect("Bild-Regex ist ein festes, gueltiges Muster")
    })
}

/// Entspricht `strip_media(text)`.
pub fn strip_media(text: &str) -> String {
    image_pattern().replace_all(text, " ").into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn removes_markdown_images_but_keeps_surrounding_text() {
        let input = "Vorher ![alt text](data:image/png;base64,AAAA) nachher";
        let result = strip_media(input);
        assert_eq!(result, "Vorher   nachher");
    }
}
