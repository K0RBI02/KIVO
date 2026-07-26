//! KIVO Search Engine (Rust-Port)
//! Scorer
//!
//! 1:1-Port von `src/engine/search/pipeline/scorer.py`.
//!
//! Prioritaet laut Original-Spec (absteigend): Titel > Inhalt > erkannte
//! Keywords (Konzept-Bonus) > Fuzzy/Prefix > Synonyme > manuelle Links
//! (betrifft link_suggester, nicht hier) > Benutzerverhalten (Bonus,
//! ueberholt NIE einen inhaltlich besseren Treffer) > Aktualitaet (Bonus).
//!
//! WICHTIGE DETAIL-TREUE: der "Konzept-Bonus" prueft im Original per
//! Python's `in`-Operator, ob ein normalisierter Query-Term als SUBSTRING
//! im (rohen, lowercased) Titel/Inhalt vorkommt - das ist bewusst KEIN
//! Token-Vergleich wie in SearchStage, sondern ein einfacher String-
//! Contains-Check. Das ist hier 1:1 uebernommen (`.contains()` statt
//! Token-Abgleich), auch wenn das auf den ersten Blick inkonsistent zur
//! SearchStage-Logik wirkt - es ist so im Original.

use chrono::{DateTime, Utc};

use crate::engine::learning::BehaviorMemory;
use crate::engine::pipeline::context::PipelineContext;

pub const TITLE_WEIGHT: f64 = 5.0;
pub const CONTENT_WEIGHT: f64 = 2.0;
pub const PREFIX_WEIGHT: f64 = 1.8;
pub const FUZZY_WEIGHT: f64 = 1.5;
pub const SYNONYM_WEIGHT: f64 = 1.0;
pub const PHRASE_BONUS: f64 = 3.0;
pub const RECENCY_MAX_BONUS: f64 = 0.5;

pub struct Scorer<'a> {
    behavior: Option<&'a BehaviorMemory>,
}

impl<'a> Scorer<'a> {
    pub fn new(behavior: Option<&'a BehaviorMemory>) -> Self {
        Self { behavior }
    }

    /// Entspricht `Scorer.execute(context)`.
    pub fn execute(&self, context: &mut PipelineContext) {
        let mut scores = std::collections::HashMap::new();

        for (entry_id, candidate) in context.candidates.iter() {
            let mut score = 0.0f64;

            score += (candidate.title_hits as f64).ln_1p() * TITLE_WEIGHT;
            score += (candidate.content_hits as f64).ln_1p() * CONTENT_WEIGHT;
            score += candidate.prefix_hits.len() as f64 * PREFIX_WEIGHT;
            score += candidate.synonym_hits.len() as f64 * SYNONYM_WEIGHT;

            for (_term, _matched, ratio) in &candidate.fuzzy_hits {
                score += ratio * FUZZY_WEIGHT;
            }

            if candidate.phrase_match {
                score += PHRASE_BONUS;
            }

            let title_lower = candidate.entry.title.to_lowercase();
            let content_lower = candidate.entry.content.to_lowercase();
            let mut concept_bonus = 0.0f64;
            for term in &context.normalized_tokens {
                if title_lower.contains(term.as_str()) || content_lower.contains(term.as_str()) {
                    let weight = context.weighted_tokens.get(term).copied().unwrap_or(1.0);
                    concept_bonus += weight - 1.0;
                }
            }
            score += concept_bonus;

            score += Self::recency_bonus(candidate.entry.last_modified);

            if let Some(behavior) = self.behavior {
                score += behavior.bonus_for(&context.raw_query, *entry_id);
            }

            scores.insert(*entry_id, score);
        }

        context.scores = scores;
    }

    fn recency_bonus(last_modified: DateTime<Utc>) -> f64 {
        let age_days = (Utc::now() - last_modified).num_days();
        if age_days <= 0 {
            return RECENCY_MAX_BONUS;
        }
        (RECENCY_MAX_BONUS * (1.0 - age_days as f64 / 30.0)).max(0.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::discovery::discover;
    use crate::engine::entry::Entry;
    use crate::engine::pipeline::keyword_extractor::KeywordExtractor;
    use crate::engine::pipeline::result_builder::ResultBuilder;
    use crate::engine::pipeline::search_stage::SearchStage;
    use crate::engine::pipeline::stopwords::all_stopwords;
    use crate::engine::pipeline::{normalizer, tokenizer};
    use crate::engine::repository::EntryRepository;
    use crate::engine::synonyms::SynonymDictionary;
    use chrono::Duration;

    fn build_repo() -> (EntryRepository, uuid::Uuid, uuid::Uuid, uuid::Uuid) {
        let mut repo = EntryRepository::new();

        let mut e1 = Entry::new(
            "Caddy Installation".to_string(),
            "Caddy auf Fedora installieren. sudo dnf install caddy. Reverse Proxy konfigurieren."
                .to_string(),
        );
        e1.last_modified = Utc::now() - Duration::days(1);
        let e1 = repo.create(e1);

        let mut e2 = Entry::new(
            "Docker Commands".to_string(),
            "Wichtige Docker Befehle: docker ps, docker compose up -d. Docker Compose fuer Multi-Container Setups."
                .to_string(),
        );
        e2.last_modified = Utc::now() - Duration::days(10);
        let e2 = repo.create(e2);

        let mut e3 = Entry::new(
            "Fedora Befehle".to_string(),
            "Fedora nutzt dnf statt apt. dnf install, dnf update. Firewall mit firewall-cmd."
                .to_string(),
        );
        e3.last_modified = Utc::now() - Duration::days(40);
        let e3 = repo.create(e3);

        (repo, e1.id, e2.id, e3.id)
    }

    fn full_search(
        repo: &EntryRepository,
        synonyms: &SynonymDictionary,
        analysis: &crate::engine::analysis::Analysis,
        behavior: Option<&BehaviorMemory>,
        raw_query: &str,
    ) -> PipelineContext {
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

        KeywordExtractor::new(analysis).execute(&mut context);
        SearchStage::new(repo, Some(synonyms), stopwords.clone()).execute(&mut context);
        Scorer::new(behavior).execute(&mut context);
        ResultBuilder::execute(&mut context);

        context
    }

    // Ground-Truth-Werte 1:1 aus einem echten End-to-End-Lauf der
    // Python-Pipeline uebernommen (discover + KeywordExtractor +
    // SearchStage + Scorer + ResultBuilder, siehe Konversation).

    #[test]
    fn matches_python_end_to_end_scores_and_ranking() {
        let (repo, caddy_id, docker_id, fedora_id) = build_repo();
        let analysis = discover(&repo.get_all(), &all_stopwords());
        let synonyms = SynonymDictionary::new();

        // Konzept-Gewichte pruefen (4 Konzepte mit doc_freq=2 -> alle
        // dasselbe Gewicht, da total_documents=3 fuer alle gleich ist)
        for term in ["befehl", "dnf", "fedora", "install"] {
            let w = analysis.concept_weight(term);
            assert!((w - 1.2876820724517808).abs() < 1e-9, "term={term} weight={w}");
        }

        let ctx = full_search(&repo, &synonyms, &analysis, None, "Fedora dnf installieren");
        assert_eq!(ctx.results.len(), 3);
        assert_eq!(ctx.results[0].entry.id, fedora_id);
        assert!((ctx.results[0].score - 7.5476579450232695).abs() < 1e-6);
        assert_eq!(ctx.results[1].entry.id, caddy_id);
        assert!((ctx.results[1].score - 7.009340030824621).abs() < 1e-6);
        assert_eq!(ctx.results[2].entry.id, docker_id);
        assert!((ctx.results[2].score - 1.3333333333333335).abs() < 1e-6);
    }

    #[test]
    fn behavior_bonus_can_reorder_close_results() {
        let (repo, _caddy_id, docker_id, _fedora_id) = build_repo();
        let analysis = discover(&repo.get_all(), &all_stopwords());
        let synonyms = SynonymDictionary::new();

        let mut behavior = BehaviorMemory::new();
        behavior.record_selection("docker", docker_id);
        behavior.record_selection("docker", docker_id);

        let ctx = full_search(&repo, &synonyms, &analysis, Some(&behavior), "docker");
        assert_eq!(ctx.results.len(), 1);
        assert_eq!(ctx.results[0].entry.id, docker_id);
        assert!((ctx.results[0].score - 7.792216416693005).abs() < 1e-6);
    }
}
