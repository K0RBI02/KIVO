//! KIVO Search Engine (Rust-Port)
//! Search Stage
//!
//! 1:1-Port von `src/engine/search/pipeline/search_stage.py`.
//! Aufgabe: Titel + Inhalt aller Entries durchsuchen (exakt, prefix,
//! synonym, fuzzy) und Rohtreffer sammeln. Kein Ranking hier (das macht
//! der Scorer in Phase 3).

use std::collections::HashSet;

use crate::engine::pipeline::context::{Candidate, PipelineContext};
use crate::engine::pipeline::fuzzy;
use crate::engine::pipeline::normalizer;
use crate::engine::pipeline::tokenizer;
use crate::engine::repository::EntryRepository;
use crate::engine::synonyms::SynonymDictionary;
use crate::engine::text_cleaning::strip_media;

const MIN_PREFIX_LENGTH: usize = 4;

pub struct SearchStage<'a> {
    repository: &'a EntryRepository,
    synonyms: Option<&'a SynonymDictionary>,
    stopwords: HashSet<&'static str>,
}

impl<'a> SearchStage<'a> {
    /// `stopwords` entspricht dem `stopwords`-Konstruktorparameter im
    /// Python-Original (steuert die Sprachumschaltung, siehe
    /// `pipeline::stopwords::stopwords_for`).
    pub fn new(
        repository: &'a EntryRepository,
        synonyms: Option<&'a SynonymDictionary>,
        stopwords: HashSet<&'static str>,
    ) -> Self {
        Self {
            repository,
            synonyms,
            stopwords,
        }
    }

    fn normalized_tokens(&self, text: &str) -> Vec<String> {
        let cleaned = strip_media(text);
        tokenizer::tokenize(&cleaned)
            .into_iter()
            .filter(|t| !self.stopwords.contains(t.as_str()))
            .map(|t| normalizer::normalize(&t))
            .collect()
    }

    /// Entspricht `SearchStage.execute(context)`.
    pub fn execute(&self, context: &mut PipelineContext) {
        // Python: `context.normalized_tokens or context.filtered_tokens`
        // Bewusst als eigene, geklonte Vec (nicht als Referenz in die
        // context-Felder) gehalten - so entsteht keinerlei Ueberschneidung
        // mit dem spaeteren `context.candidates.insert(...)` weiter unten
        // im selben Funktionskoerper.
        let query_terms: Vec<String> = if !context.normalized_tokens.is_empty() {
            context.normalized_tokens.clone()
        } else {
            context.filtered_tokens.clone()
        };

        let phrase = context.filtered_tokens.join(" ").trim().to_string();

        for entry in self.repository.get_all() {
            let title_tokens = self.normalized_tokens(&entry.title);
            let content_tokens = self.normalized_tokens(&entry.content);

            let all_tokens: HashSet<String> = title_tokens
                .iter()
                .cloned()
                .chain(content_tokens.iter().cloned())
                .collect();

            let mut title_hits = 0usize;
            let mut content_hits = 0usize;
            let mut prefix_hits: Vec<String> = Vec::new();
            let mut synonym_hits: Vec<(String, String)> = Vec::new();
            let mut fuzzy_hits: Vec<(String, String, f64)> = Vec::new();

            for term in &query_terms {
                if title_tokens.iter().any(|t| t == term) {
                    title_hits += title_tokens.iter().filter(|t| *t == term).count();
                    continue;
                }
                if content_tokens.iter().any(|t| t == term) {
                    content_hits += content_tokens.iter().filter(|t| *t == term).count();
                    continue;
                }

                let term_char_len = term.chars().count();
                let mut handled = false;

                if term_char_len >= MIN_PREFIX_LENGTH {
                    // Iterationsreihenfolge ueber ein HashSet ist wie bei
                    // Python's `set` nicht deterministisch garantiert -
                    // gleiches Verhalten wie das Original.
                    let prefix_match = all_tokens.iter().find(|t| {
                        t.chars().count() >= MIN_PREFIX_LENGTH
                            && (t.starts_with(term.as_str()) || term.starts_with(t.as_str()))
                    });
                    if prefix_match.is_some() {
                        prefix_hits.push(term.clone());
                        handled = true;
                    }
                }

                if !handled {
                    if let Some(synonyms) = self.synonyms {
                        let mut expanded = synonyms.expand(term);
                        expanded.remove(term);
                        let matched_synonym =
                            expanded.iter().find(|s| all_tokens.contains(s.as_str()));
                        if let Some(matched) = matched_synonym {
                            synonym_hits.push((term.clone(), matched.clone()));
                            handled = true;
                        }
                    }
                }

                if !handled {
                    let candidates: Vec<String> = all_tokens.iter().cloned().collect();
                    if let Some((matched, score)) =
                        fuzzy::best_fuzzy_match(term, &candidates, fuzzy::DEFAULT_THRESHOLD)
                    {
                        fuzzy_hits.push((term.clone(), matched, score));
                    }
                }
            }

            let phrase_match = !phrase.is_empty()
                && phrase.chars().count() >= 6
                && (entry.title.to_lowercase().contains(&phrase)
                    || entry.content.to_lowercase().contains(&phrase));

            if title_hits > 0
                || content_hits > 0
                || !prefix_hits.is_empty()
                || !synonym_hits.is_empty()
                || !fuzzy_hits.is_empty()
                || phrase_match
            {
                context.candidates.insert(
                    entry.id,
                    Candidate {
                        entry: entry.clone(),
                        title_hits,
                        content_hits,
                        prefix_hits,
                        synonym_hits,
                        fuzzy_hits,
                        phrase_match,
                    },
                );
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::entry::Entry;
    use crate::engine::pipeline::stopwords::all_stopwords;

    fn build_repo() -> EntryRepository {
        let mut repo = EntryRepository::new();
        repo.create(Entry::new(
            "Caddy Installation".to_string(),
            "Caddy auf Fedora installieren. sudo dnf install caddy. Reverse Proxy konfigurieren."
                .to_string(),
        ));
        repo.create(Entry::new(
            "Docker Commands".to_string(),
            "Wichtige Docker Befehle: docker ps, docker compose up -d.".to_string(),
        ));
        repo
    }

    fn run_query(repo: &EntryRepository, synonyms: &SynonymDictionary, raw_query: &str) -> PipelineContext {
        let stopwords = all_stopwords();
        let tokens = tokenizer::tokenize(raw_query);
        let filtered_tokens: Vec<String> = tokens
            .iter()
            .filter(|t| !stopwords.contains(t.as_str()))
            .cloned()
            .collect();
        let normalized_tokens: Vec<String> =
            filtered_tokens.iter().map(|t| normalizer::normalize(t)).collect();

        let mut context = PipelineContext::new(raw_query.to_string());
        context.tokens = tokens;
        context.filtered_tokens = filtered_tokens;
        context.normalized_tokens = normalized_tokens;

        let stage = SearchStage::new(repo, Some(synonyms), stopwords.clone());
        stage.execute(&mut context);
        context
    }

    // Alle vier Szenarien + Erwartungswerte 1:1 gegen die echte
    // Python-SearchStage verifiziert (siehe Konversation).

    #[test]
    fn exact_title_and_content_hits() {
        let repo = build_repo();
        let synonyms = SynonymDictionary::new();
        let ctx = run_query(&repo, &synonyms, "Caddy Fedora installieren");

        let caddy_entry = repo.get_all().into_iter().find(|e| e.title == "Caddy Installation").unwrap();
        let candidate = ctx.candidates.get(&caddy_entry.id).expect("Caddy-Eintrag sollte Treffer sein");
        assert_eq!(candidate.title_hits, 2);
        assert_eq!(candidate.content_hits, 1);
        assert!(candidate.prefix_hits.is_empty());
        assert!(!candidate.phrase_match);

        // Docker-Eintrag darf hier KEIN Kandidat sein
        let docker_entry = repo.get_all().into_iter().find(|e| e.title == "Docker Commands").unwrap();
        assert!(ctx.candidates.get(&docker_entry.id).is_none());
    }

    #[test]
    fn fuzzy_fragment_matches_content() {
        let repo = build_repo();
        let synonyms = SynonymDictionary::new();
        let ctx = run_query(&repo, &synonyms, "proxy-dings");

        let caddy_entry = repo.get_all().into_iter().find(|e| e.title == "Caddy Installation").unwrap();
        let candidate = ctx.candidates.get(&caddy_entry.id).expect("sollte per Fuzzy/Content matchen");
        assert_eq!(candidate.title_hits, 0);
        assert_eq!(candidate.content_hits, 1);
    }

    #[test]
    fn stemmer_quirk_produces_prefix_and_phrase_match() {
        // Eigenheit des heuristischen Stemmers: "reverse" -> "revers",
        // aber "revers" (Query) -> "rever" - beide Stemme sind
        // UNTERSCHIEDLICH, deshalb kein direkter Treffer, sondern ein
        // Prefix-Match auf "rever" plus ein Phrase-Match (weil "revers"
        // als Substring in "reverse" auftaucht). Exakt so verhaelt sich
        // auch das Python-Original - keine Rust-Abweichung, sondern eine
        // treu portierte Eigenart des Original-Stemmers.
        let repo = build_repo();
        let synonyms = SynonymDictionary::new();
        let ctx = run_query(&repo, &synonyms, "revers");

        let caddy_entry = repo.get_all().into_iter().find(|e| e.title == "Caddy Installation").unwrap();
        let candidate = ctx.candidates.get(&caddy_entry.id).expect("sollte matchen");
        assert_eq!(candidate.title_hits, 0);
        assert_eq!(candidate.content_hits, 0);
        assert_eq!(candidate.prefix_hits, vec!["rever".to_string()]);
        assert!(candidate.phrase_match);
    }

    #[test]
    fn multi_word_query_counts_hits_across_title_and_content() {
        let repo = build_repo();
        let synonyms = SynonymDictionary::new();
        let ctx = run_query(&repo, &synonyms, "docker ps up");

        let docker_entry = repo.get_all().into_iter().find(|e| e.title == "Docker Commands").unwrap();
        let candidate = ctx.candidates.get(&docker_entry.id).expect("sollte matchen");
        assert_eq!(candidate.title_hits, 1);
        assert_eq!(candidate.content_hits, 2);
    }
}
