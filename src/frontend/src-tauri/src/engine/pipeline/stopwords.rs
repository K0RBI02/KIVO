//! KIVO Search Engine (Rust-Port)
//! Stopword Filter
//!
//! 1:1-Port von `src/engine/search/pipeline/stopwords.py`.
//! Wortlisten unveraendert uebernommen (Reihenfolge spielt bei einem Set
//! keine Rolle, nur die Mitgliedschaft zaehlt).

use std::collections::HashSet;

pub const GERMAN_STOPWORDS: &[&str] = &[
    "der", "die", "das", "und", "oder", "ist", "war", "wie", "was", "wo", "ich", "du", "er",
    "sie", "es", "wir", "ihr", "mich", "dich", "mir", "dir", "mit", "auf", "fuer", "für", "von",
    "zu", "im", "in", "ein", "eine", "einen", "einem", "einer", "hab", "habe", "hatte", "hatten",
    "nicht", "auch", "mal", "dieses", "diese", "dieser", "noch", "so", "als", "an", "am", "bei",
    "aus", "nach", "ueber", "über", "unter", "durch", "um", "ohne", "gegen", "bis", "seit",
    "nochmal", "nochmals", "wieder", "man", "kann", "muss", "soll", "wird", "werden", "sein",
    "haben", "dann", "hier", "dort", "da", "hierzu", "davon", "dabei",
];

pub const ENGLISH_STOPWORDS: &[&str] = &[
    "the", "a", "an", "is", "was", "how", "what", "where", "i", "you", "he", "she", "it", "we",
    "they", "with", "on", "for", "of", "to", "in", "not", "also", "again", "this", "that",
    "these", "those", "can", "must", "should", "will", "be", "have", "then", "my", "me",
];

pub fn german_stopwords() -> HashSet<&'static str> {
    GERMAN_STOPWORDS.iter().copied().collect()
}

pub fn english_stopwords() -> HashSet<&'static str> {
    ENGLISH_STOPWORDS.iter().copied().collect()
}

/// Entspricht Python's `STOPWORDS = GERMAN_STOPWORDS | ENGLISH_STOPWORDS`.
pub fn all_stopwords() -> HashSet<&'static str> {
    german_stopwords()
        .into_iter()
        .chain(english_stopwords())
        .collect()
}

/// Entspricht `language.available_languages()`.
pub fn available_languages() -> Vec<&'static str> {
    vec!["auto", "de", "en"]
}

/// Entspricht `language.stopwords_for(lang)`.
/// "de" -> nur deutsche Stopwords, "en" -> nur englische, alles andere
/// (inkl. "auto", dem Default) -> die kombinierte Liste.
///
/// SCOPE-HINWEIS: Python's `language.normalizer_for(lang)` wuerde bei "de"/
/// "en" zusaetzlich auf einen praeziseren Snowball-Stemmer umschalten -
/// aber NUR, falls das optionale Paket `snowballstemmer` installiert ist
/// (sonst faellt Python selbst auf denselben heuristischen Normalizer
/// zurueck, den wir hier immer verwenden). Dieser Rust-Port bildet aktuell
/// den Fall "kein Snowball installiert" ab, also Python's eigenes
/// Default-/Fallback-Verhalten. Falls bei euch tatsaechlich
/// `snowballstemmer` im Python-venv installiert war, wuerde die deutsche/
/// englische Stemming-Praezision hier leicht abweichen - dann bitte
/// Bescheid geben, das liesse sich mit dem Rust-Crate `rust-stemmers`
/// gezielt nachruesten.
pub fn stopwords_for(language: &str) -> HashSet<&'static str> {
    match language {
        "de" => german_stopwords(),
        "en" => english_stopwords(),
        _ => all_stopwords(),
    }
}
