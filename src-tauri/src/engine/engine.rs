//! KIVO Search Engine (Rust-Port)
//! KnowledgeEngine
//!
//! 1:1-Port von `src/engine/search/engine.py`.
//! Die EINZIGE Anlaufstelle fuer den Client (hier: die Tauri-Commands in
//! commands.rs). Genau wie im Python-Original soll niemand ausserhalb
//! dieser Fassade selbst suchen, ranken, sortieren oder Empfehlungen
//! berechnen.
//!
//! SCOPE-HINWEISE (siehe auch die einzelnen Modul-Dateien):
//! - `related_concepts()` (Graph-Zugriff) wurde NICHT portiert - im
//!   Original toter Code, siehe link_suggester.rs.
//! - Sprachumschaltung ("auto"/"de"/"en") wirkt auf die Stopword-Filterung,
//!   der Normalizer bleibt immer heuristisch (kein Snowball-Support),
//!   siehe pipeline::stopwords.

use std::collections::HashSet;
use std::io;
use std::path::Path;

use uuid::Uuid;

use crate::engine::analysis::Analysis;
use crate::engine::discovery::discover;
use crate::engine::entry::Entry;
use crate::engine::learning::BehaviorMemory;
use crate::engine::link_suggester::suggest_links;
use crate::engine::pipeline::context::{PipelineContext, SearchResult};
use crate::engine::pipeline::keyword_extractor::KeywordExtractor;
use crate::engine::pipeline::normalizer;
use crate::engine::pipeline::result_builder::ResultBuilder;
use crate::engine::pipeline::scorer::Scorer;
use crate::engine::pipeline::search_stage::SearchStage;
use crate::engine::pipeline::stopwords::{available_languages, stopwords_for};
use crate::engine::pipeline::tokenizer;
use crate::engine::entry::Link;
use crate::engine::repository::EntryRepository;
use crate::engine::store::EntryStore;
use crate::engine::synonyms::SynonymDictionary;

pub struct KnowledgeEngine {
    pub repository: EntryRepository,
    pub analysis: Analysis,
    pub synonyms: SynonymDictionary,
    pub behavior: BehaviorMemory,
    pub language: String,
    auto_save: bool,
    store: EntryStore,
}

impl KnowledgeEngine {
    /// Entspricht `KnowledgeEngine(data_dir, auto_save, language)`.
    pub fn new(data_dir: impl AsRef<Path>, auto_save: bool, language: &str) -> io::Result<Self> {
        let store = EntryStore::new(data_dir)?;

        let mut engine = Self {
            repository: EntryRepository::new(),
            analysis: Analysis::new(),
            synonyms: SynonymDictionary::new(),
            behavior: BehaviorMemory::new(),
            language: language.to_string(),
            auto_save,
            store,
        };

        engine.load_from_disk();
        Ok(engine)
    }

    fn current_stopwords(&self) -> HashSet<&'static str> {
        stopwords_for(&self.language)
    }

    // -------- Sprache --------

    /// Entspricht `set_language(language)`.
    pub fn set_language(&mut self, language: &str) {
        self.language = language.to_string();
        self.rebuild_analysis();
    }

    /// Entspricht `available_languages()`.
    pub fn available_languages_list(&self) -> Vec<&'static str> {
        available_languages()
    }

    // -------- Persistenz --------

    fn load_from_disk(&mut self) {
        let entries = self.store.load_all();
        for entry in entries {
            self.repository.create(entry);
        }
        self.rebuild_analysis();
    }

    /// Entspricht `save()`.
    pub fn save(&self) -> io::Result<()> {
        self.store.save_all(&self.repository.get_all())
    }

    fn maybe_save(&self) -> io::Result<()> {
        if self.auto_save {
            self.save()
        } else {
            Ok(())
        }
    }

    /// Entspricht `clear_all()`.
    pub fn clear_all(&mut self) -> io::Result<()> {
        self.repository = EntryRepository::new();
        self.behavior = BehaviorMemory::new();
        self.rebuild_analysis();
        self.maybe_save()
    }

    /// Entspricht `export_all()`.
    pub fn export_all(&self) -> Vec<Entry> {
        self.repository.get_all()
    }

    /// Entspricht `import_entries(items)`. `items` sind (title, content)-
    /// Paare (im Original ein Dict mit .get("title","")/.get("content","")).
    pub fn import_entries(&mut self, items: &[(String, String)]) -> io::Result<usize> {
        let mut count = 0usize;
        for (title, content) in items {
            let trimmed_title = title.trim();
            if trimmed_title.is_empty() {
                continue;
            }
            self.repository
                .create(Entry::new(trimmed_title.to_string(), content.clone()));
            count += 1;
        }
        self.rebuild_analysis();
        self.maybe_save()?;
        Ok(count)
    }

    // -------- CRUD --------

    /// Entspricht `create(title, content)`.
    pub fn create(&mut self, title: String, content: String) -> io::Result<Entry> {
        let entry = Entry::new(title, content);
        let created = self.repository.create(entry);
        self.rebuild_analysis();
        self.maybe_save()?;
        Ok(created)
    }

    /// Entspricht `update(entry_id, title=None, content=None)`.
    pub fn update(
        &mut self,
        entry_id: Uuid,
        title: Option<String>,
        content: Option<String>,
    ) -> io::Result<Option<Entry>> {
        let mut entry = match self.repository.get(entry_id) {
            Some(e) => e,
            None => return Ok(None),
        };
        if let Some(t) = title {
            entry.title = t;
        }
        if let Some(c) = content {
            entry.content = c;
        }
        let updated = self.repository.update(entry);
        self.rebuild_analysis();
        self.maybe_save()?;
        Ok(Some(updated))
    }

    /// Entspricht `delete(entry_id)`.
    pub fn delete(&mut self, entry_id: Uuid) -> io::Result<()> {
        self.repository.delete(entry_id);
        self.rebuild_analysis();
        self.maybe_save()
    }

    pub fn get(&self, entry_id: Uuid) -> Option<Entry> {
        self.repository.get(entry_id)
    }

    pub fn get_all(&self) -> Vec<Entry> {
        self.repository.get_all()
    }

    /// Entspricht `recent(limit)`.
    pub fn recent(&self, limit: usize) -> Vec<Entry> {
        let mut ordered = self.repository.get_all();
        ordered.sort_by(|a, b| b.last_modified.cmp(&a.last_modified));
        ordered.into_iter().take(limit).collect()
    }

    /// Entspricht `link(entry_id, target_id)` (manuellen Link hinzufuegen).
    pub fn add_manual_link(&mut self, entry_id: Uuid, target_id: Uuid) -> io::Result<()> {
        if let Some(mut entry) = self.repository.get(entry_id) {
            entry.add_manual_link(target_id);
            self.repository.update(entry);
            self.maybe_save()?;
        }
        Ok(())
    }

    // -------- Self-Discovery --------

    /// Entspricht `rebuild_analysis()`. Baut NUR die Analysis neu (kein
    /// Graph - siehe Scope-Hinweis oben).
    pub fn rebuild_analysis(&mut self) {
        let stopwords = self.current_stopwords();
        self.analysis = discover(&self.repository.get_all(), &stopwords);
    }

    // -------- Suche --------

    /// Entspricht `search(query)`.
    pub fn search(&self, query: &str) -> Vec<SearchResult> {
        let stopwords = self.current_stopwords();

        let tokens = tokenizer::tokenize(query);
        let filtered_tokens: Vec<String> = tokens
            .iter()
            .filter(|t| !stopwords.contains(t.as_str()))
            .cloned()
            .collect();
        let normalized_tokens: Vec<String> =
            filtered_tokens.iter().map(|t| normalizer::normalize(t)).collect();

        let mut context = PipelineContext::new(query.to_string());
        context.tokens = tokens;
        context.filtered_tokens = filtered_tokens;
        context.normalized_tokens = normalized_tokens;

        KeywordExtractor::new(&self.analysis).execute(&mut context);
        SearchStage::new(&self.repository, Some(&self.synonyms), stopwords).execute(&mut context);
        Scorer::new(Some(&self.behavior)).execute(&mut context);
        ResultBuilder::execute(&mut context);

        context.results
    }

    /// Entspricht `record_selection(query, entry_id)`.
    pub fn record_selection(&mut self, query: &str, entry_id: Uuid) {
        self.behavior.record_selection(query, entry_id);
    }

    // -------- Links --------

    /// Entspricht `links_for(entry_id, max_total)`.
    pub fn links_for(&self, entry_id: Uuid, max_total: usize) -> Vec<Link> {
        let entry = match self.repository.get(entry_id) {
            Some(e) => e,
            None => return Vec::new(),
        };
        let stopwords = self.current_stopwords();
        suggest_links(&entry, &self.repository.get_all(), &self.analysis, max_total, &stopwords)
    }
}
