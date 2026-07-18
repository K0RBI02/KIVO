//! KIVO Engine (Rust-Port)
//! Persistence
//!
//! 1:1-Port von `src/engine/search/persistence.py` (kombiniert mit
//! `storage/file_storage.py`, da wir in Rust keine austauschbare
//! Storage-Abstraktion brauchen - es gibt nur ein Zielformat).
//!
//! Speichert weiterhin unter `kivo_data/entries.json` als JSON-Array,
//! damit bestehende Daten aus der Python-Version unveraendert weiter
//! gelesen werden koennen.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use crate::engine::entry::Entry;

pub struct EntryStore {
    directory: PathBuf,
}

impl EntryStore {
    /// Entspricht `EntryStore(data_dir)`. Legt das Verzeichnis an, falls es
    /// noch nicht existiert (gleiches Verhalten wie Python's `Path.mkdir`).
    pub fn new(directory: impl AsRef<Path>) -> io::Result<Self> {
        let directory = directory.as_ref().to_path_buf();
        fs::create_dir_all(&directory)?;
        Ok(Self { directory })
    }

    fn file_path(&self) -> PathBuf {
        self.directory.join("entries.json")
    }

    /// Entspricht `EntryStore.load_all()`. Gibt eine leere Liste zurueck,
    /// falls die Datei (noch) nicht existiert oder nicht lesbar ist - genau
    /// wie das Python-Original bei fehlendem Payload.
    pub fn load_all(&self) -> Vec<Entry> {
        let path = self.file_path();
        if !path.exists() {
            return Vec::new();
        }

        let content = match fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => return Vec::new(),
        };

        serde_json::from_str::<Vec<Entry>>(&content).unwrap_or_default()
    }

    /// Entspricht `EntryStore.save_all()`.
    pub fn save_all(&self, entries: &[Entry]) -> io::Result<()> {
        let json = serde_json::to_string_pretty(entries)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
        fs::write(self.file_path(), json)
    }
}
