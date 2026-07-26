//! KIVO Desktop (Tauri)
//! Commands
//!
//! Ersetzt die bisherige HTTP-API (webapp/server.py + api.ts fetch()-
//! Aufrufe) durch native Tauri-Commands. Kein Webserver, kein GET/POST,
//! kein separater Prozess mehr - das Frontend ruft diese Funktionen direkt
//! per `invoke("command_name", {...})` auf.
//!
//! Jeder Command entspricht 1:1 einer Route aus `webapp/server.py` /
//! Funktion aus `api.ts` - siehe Kommentar je Command.

use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use tauri::State;
use uuid::Uuid;

use crate::engine::engine::KnowledgeEngine;
use crate::engine::entry::{Entry, Link};
use crate::engine::pipeline::context::SearchResult;

pub type EngineState = Mutex<KnowledgeEngine>;

fn parse_uuid(id: &str) -> Result<Uuid, String> {
    Uuid::parse_str(id).map_err(|_| format!("Ungueltige ID: {id}"))
}

/// Wire-Format fuer Entries Richtung Frontend. Entspricht bewusst
/// `entry_to_json()` aus dem alten `webapp/server.py` (NICHT dem internen
/// Speicherformat aus persistence.py/entry.rs): `manual_links` wird zu
/// einer reinen Liste von Ziel-IDs vereinfacht, statt der vollen
/// `{target_id, kind, score}`-Objekte. Das war schon im Python-Original
/// eine bewusste, separate Serialisierungsschicht - hier 1:1 nachgebaut.
#[derive(Debug, Serialize)]
pub struct EntryDto {
    pub id: String,
    pub title: String,
    pub content: String,
    pub last_modified: String,
    pub manual_links: Vec<String>,
}

impl From<Entry> for EntryDto {
    fn from(entry: Entry) -> Self {
        Self {
            id: entry.id.to_string(),
            title: entry.title,
            content: entry.content,
            last_modified: entry.last_modified.to_rfc3339(),
            manual_links: entry
                .manual_links
                .into_iter()
                .map(|l| l.target_id.to_string())
                .collect(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct SearchResultDto {
    pub entry: EntryDto,
    pub score: f64,
}

impl From<SearchResult> for SearchResultDto {
    fn from(result: SearchResult) -> Self {
        Self {
            entry: result.entry.into(),
            score: result.score,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct LanguageInfoDto {
    pub current: String,
    pub available: Vec<String>,
    pub snowball_available: bool,
}

/// Entspricht dem Item-Shape, das `POST /api/import` bisher akzeptiert hat.
#[derive(Debug, Deserialize)]
pub struct ImportItem {
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub content: String,
}

/// Entspricht `GET /api/entries` / `api.getAll()`.
#[tauri::command]
pub fn get_all_entries(state: State<EngineState>) -> Vec<EntryDto> {
    state
        .lock()
        .unwrap()
        .get_all()
        .into_iter()
        .map(EntryDto::from)
        .collect()
}

/// Entspricht `GET /api/recent?limit=` / `api.recent(limit)`.
#[tauri::command]
pub fn get_recent(limit: usize, state: State<EngineState>) -> Vec<EntryDto> {
    state
        .lock()
        .unwrap()
        .recent(limit)
        .into_iter()
        .map(EntryDto::from)
        .collect()
}

/// Entspricht `GET /api/entries/<id>` / `api.get(id)`.
#[tauri::command]
pub fn get_entry(id: String, state: State<EngineState>) -> Result<EntryDto, String> {
    let uuid = parse_uuid(&id)?;
    state
        .lock()
        .unwrap()
        .get(uuid)
        .map(EntryDto::from)
        .ok_or_else(|| "Eintrag nicht gefunden".to_string())
}

/// Entspricht `GET /api/search?q=` / `api.search(query)`.
#[tauri::command]
pub fn search_entries(query: String, state: State<EngineState>) -> Vec<SearchResultDto> {
    state
        .lock()
        .unwrap()
        .search(&query)
        .into_iter()
        .map(SearchResultDto::from)
        .collect()
}

/// Entspricht `POST /api/entries` / `api.create(title, content)`.
#[tauri::command]
pub fn create_entry(
    title: String,
    content: String,
    state: State<EngineState>,
) -> Result<EntryDto, String> {
    state
        .lock()
        .unwrap()
        .create(title, content)
        .map(EntryDto::from)
        .map_err(|e| e.to_string())
}

/// Entspricht `POST /api/entries/<id>` / `api.update(id, title, content)`.
#[tauri::command]
pub fn update_entry(
    id: String,
    title: String,
    content: String,
    state: State<EngineState>,
) -> Result<EntryDto, String> {
    let uuid = parse_uuid(&id)?;
    state
        .lock()
        .unwrap()
        .update(uuid, Some(title), Some(content))
        .map_err(|e| e.to_string())?
        .map(EntryDto::from)
        .ok_or_else(|| "Eintrag nicht gefunden".to_string())
}

/// Entspricht `DELETE /api/entries/<id>` / `api.remove(id)`.
#[tauri::command]
pub fn delete_entry(id: String, state: State<EngineState>) -> Result<(), String> {
    let uuid = parse_uuid(&id)?;
    state.lock().unwrap().delete(uuid).map_err(|e| e.to_string())
}

/// Entspricht `GET /api/entries/<id>/links` / `api.linksFor(id)`.
/// Kein DTO noetig - `Link` serialisiert bereits exakt im Format, das
/// `ApiLink` im Frontend erwartet (`{target_id, kind, score}`).
#[tauri::command]
pub fn get_links_for(id: String, state: State<EngineState>) -> Result<Vec<Link>, String> {
    let uuid = parse_uuid(&id)?;
    Ok(state.lock().unwrap().links_for(uuid, 3))
}

/// Entspricht `POST /api/select` / `api.recordSelection(query, entryId)`.
#[tauri::command]
pub fn record_selection(
    query: String,
    entry_id: String,
    state: State<EngineState>,
) -> Result<(), String> {
    let uuid = parse_uuid(&entry_id)?;
    state.lock().unwrap().record_selection(&query, uuid);
    Ok(())
}

/// Entspricht `POST /api/link/<id>` / `api.addManualLink(entryId, targetId)`.
#[tauri::command]
pub fn add_manual_link(
    entry_id: String,
    target_id: String,
    state: State<EngineState>,
) -> Result<(), String> {
    let eid = parse_uuid(&entry_id)?;
    let tid = parse_uuid(&target_id)?;
    state
        .lock()
        .unwrap()
        .add_manual_link(eid, tid)
        .map_err(|e| e.to_string())
}

/// Entspricht `GET /api/export` / `api.exportAll()`.
#[tauri::command]
pub fn export_all_entries(state: State<EngineState>) -> Vec<EntryDto> {
    state
        .lock()
        .unwrap()
        .export_all()
        .into_iter()
        .map(EntryDto::from)
        .collect()
}

/// Entspricht `POST /api/import` / `api.importEntries(entries)`.
#[tauri::command]
pub fn import_entries(
    entries: Vec<ImportItem>,
    state: State<EngineState>,
) -> Result<usize, String> {
    let items: Vec<(String, String)> =
        entries.into_iter().map(|e| (e.title, e.content)).collect();
    state
        .lock()
        .unwrap()
        .import_entries(&items)
        .map_err(|e| e.to_string())
}

/// Entspricht `DELETE /api/entries` / `api.deleteAll()`.
#[tauri::command]
pub fn delete_all_entries(state: State<EngineState>) -> Result<(), String> {
    state.lock().unwrap().clear_all().map_err(|e| e.to_string())
}

/// Entspricht `GET /api/language` / `api.getLanguage()`.
/// `snowball_available` ist immer `false` - siehe Scope-Hinweis in
/// pipeline/stopwords.rs (kein Snowball-Stemmer-Support in diesem Port).
#[tauri::command]
pub fn get_language_info(state: State<EngineState>) -> LanguageInfoDto {
    let engine = state.lock().unwrap();
    LanguageInfoDto {
        current: engine.language.clone(),
        available: engine
            .available_languages_list()
            .into_iter()
            .map(|s| s.to_string())
            .collect(),
        snowball_available: false,
    }
}

/// Entspricht `POST /api/language` / `api.setLanguage(lang)`.
#[tauri::command]
pub fn set_language(language: String, state: State<EngineState>) -> Result<(), String> {
    state.lock().unwrap().set_language(&language);
    Ok(())
}

