//! KIVO Search Engine (Rust-Port)
//! Keyword Extractor
//!
//! 1:1-Port von `src/engine/search/pipeline/keyword_extractor.py`.
//! Aufgabe: Query-Tokens gewichten. Bekannte "Konzepte" (von der Discovery
//! entdeckt) bekommen mehr Gewicht als Zufallswoerter.

use std::collections::HashMap;

use crate::engine::analysis::Analysis;
use crate::engine::pipeline::context::PipelineContext;

pub struct KeywordExtractor<'a> {
    analysis: &'a Analysis,
}

impl<'a> KeywordExtractor<'a> {
    pub fn new(analysis: &'a Analysis) -> Self {
        Self { analysis }
    }

    /// Entspricht `KeywordExtractor.execute(context)`.
    pub fn execute(&self, context: &mut PipelineContext) {
        let mut weighted: HashMap<String, f64> = HashMap::new();
        for term in &context.normalized_tokens {
            weighted.insert(term.clone(), self.analysis.concept_weight(term));
        }
        context.weighted_tokens = weighted;
    }
}
