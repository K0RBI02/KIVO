//! KIVO Search Engine (Rust-Port)
//! Normalizer
//!
//! 1:1-Port von `src/engine/search/pipeline/normalizer.py`.
//! Heuristischer Leicht-Stemmer, kein Woerterbuch - bewusst so im Original,
//! siehe Docstring dort.
//!
//! WICHTIG fuer Korrektheit (der Grund, warum das hier nicht einfach ein
//! naiver String-Slice ist): Python's `len(word)` zaehlt Unicode-Zeichen,
//! nicht Bytes. Deutsche Umlaute (ä/ö/ü/ß) sind in UTF-8 aber 2 Byte lang.
//! Wuerde man hier stattdessen `word.len()` (Byte-Laenge) fuer die
//! Mindestlaengen-Pruefung verwenden, koennten Woerter mit Umlauten nahe der
//! Grenze (MIN_STEM_LENGTH) ein anderes Ergebnis liefern als im Python-
//! Original. Deshalb wird hier bewusst mit `chars().count()` gearbeitet.
//! Das eigentliche Abschneiden (Byte-Slice) ist trotzdem sicher, weil alle
//! Suffixe in der Liste reines ASCII sind - ein ASCII-Byte kann in UTF-8
//! nie ein Fortsetzungsbyte eines Mehrbyte-Zeichens sein, das gefundene
//! Suffix-Ende liegt also immer exakt auf einer Zeichen-Grenze.

// Reihenfolge wichtig (identisch zu Python): laengere/speziellere Endungen
// zuerst pruefen, sonst wird zu frueh (und falsch) gekuerzt.
const GERMAN_SUFFIXES: &[&str] = &[
    "ierungen", "ierung", "ationen", "ation", "ieren", "iert", "ungen", "ung", "heiten", "heit",
    "keiten", "keit", "en", "er", "es", "e", "s",
];

const MIN_STEM_LENGTH: usize = 3;

/// Entspricht `Normalizer.normalize(token)`.
pub fn normalize(token: &str) -> String {
    let word = token.to_lowercase();
    let word_char_len = word.chars().count();

    for suffix in GERMAN_SUFFIXES {
        if word.ends_with(suffix) {
            // Suffixe sind reines ASCII, also gilt char_len == byte_len.
            let suffix_char_len = suffix.len();
            if word_char_len >= suffix_char_len
                && word_char_len - suffix_char_len >= MIN_STEM_LENGTH
            {
                let cut_at_byte = word.len() - suffix.len();
                return word[..cut_at_byte].to_string();
            }
        }
    }

    word
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn strips_known_suffix_when_stem_long_enough() {
        assert_eq!(normalize("Installation"), "install");
        // "ieren" wird VOR "en"/"er" geprueft (Reihenfolge der Suffixliste),
        // deshalb "install" und nicht "installier".
        assert_eq!(normalize("installieren"), "install");
    }

    #[test]
    fn keeps_word_when_stem_would_be_too_short() {
        // "es" hat Suffix "es" -> Stamm waere "" (0 Zeichen) -> zu kurz, bleibt "es"
        assert_eq!(normalize("es"), "es");
    }

    #[test]
    fn counts_umlauts_as_single_characters_for_min_length() {
        // "Größe" -> lowercase "größe" (5 Zeichen, 6 Bytes wegen ö).
        // Suffix "e" (1 Zeichen) passt: Stamm "größ" hat 4 Zeichen >= 3 -> wird gekuerzt.
        assert_eq!(normalize("Größe"), "größ");
    }
}
