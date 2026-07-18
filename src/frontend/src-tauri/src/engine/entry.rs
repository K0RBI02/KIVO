//! KIVO Engine (Rust-Port)
//! Entry - das einzige Nutzer-Datenmodell.
//!
//! 1:1-Port von `src/engine/search/entry.py` + `link.py`.
//! WICHTIG fuer Bestandsdaten: die serde-Reprasentation ist bewusst so gewaehlt,
//! dass sie exakt dem JSON entspricht, das die Python-Engine bisher unter
//! `kivo_data/entries.json` geschrieben hat (gleiche Feldnamen, gleiche
//! "manual"/"suggested"-Strings) - bestehende Nutzerdaten bleiben also lesbar.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Entspricht Python's `LinkKind = Literal["manual", "suggested"]`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum LinkKind {
    Manual,
    Suggested,
}

/// Entspricht Python's `Link`-Dataclass (link.py).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Link {
    pub target_id: Uuid,
    pub kind: LinkKind,
    #[serde(default)]
    pub score: f64,
}

/// Entspricht Python's `Entry`-Dataclass (entry.py).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entry {
    pub id: Uuid,
    pub title: String,
    pub content: String,
    pub last_modified: DateTime<Utc>,
    #[serde(default)]
    pub manual_links: Vec<Link>,
}

impl Entry {
    /// Entspricht `Entry(title=..., content=...)` mit den Dataclass-Defaults
    /// (neue id, last_modified = jetzt, leere manual_links).
    pub fn new(title: String, content: String) -> Self {
        Self {
            id: Uuid::new_v4(),
            title,
            content,
            last_modified: Utc::now(),
            manual_links: Vec::new(),
        }
    }

    /// Entspricht `Entry.touch()`.
    pub fn touch(&mut self) {
        self.last_modified = Utc::now();
    }

    /// Entspricht `Entry.add_manual_link()`.
    /// Ignoriert den Aufruf, wenn dieser Link bereits existiert (gleiches
    /// Verhalten wie das Python-Original).
    pub fn add_manual_link(&mut self, target_id: Uuid) {
        if self.manual_links.iter().any(|l| l.target_id == target_id) {
            return;
        }
        self.manual_links.push(Link {
            target_id,
            kind: LinkKind::Manual,
            score: 0.0,
        });
        self.touch();
    }

    /// Entspricht `Entry.remove_manual_link()`. Aktuell von keinem Aufrufer
    /// benutzt (im Python-Original ebenfalls nicht), aber der Vollstaendigkeit
    /// halber mit portiert.
    #[allow(dead_code)]
    pub fn remove_manual_link(&mut self, target_id: Uuid) {
        self.manual_links.retain(|l| l.target_id != target_id);
        self.touch();
    }
}
