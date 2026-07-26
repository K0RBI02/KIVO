/**
 * KIVO API Client
 *
 * PHASE 6: komplett auf Tauri `invoke()` umgestellt - kein `fetch()` zu
 * einem lokalen Server mehr (`127.0.0.1:8420` existiert nicht mehr, die
 * gesamte Suchlogik laeuft jetzt nativ im Rust-Backend, siehe
 * src-tauri/src/engine/ + src-tauri/src/commands.rs).
 *
 * WICHTIG: das oeffentliche Interface (`api.getAll()`, `api.search()`,
 * ...) ist bewusst UNVERAENDERT gegenueber der alten fetch()-Version -
 * App.tsx muss dadurch an keiner Stelle angepasst werden, nur diese Datei
 * hier.
 *
 * GROESSTE UNSICHERHEIT DIESER PHASE: Tauri konvertiert Command-Argument-
 * Namen beim Aufruf aus JS automatisch von Rust's snake_case zu camelCase
 * (z.B. Rust-Parameter `entry_id` -> JS-Schluessel `entryId`). Das ist
 * dokumentiertes Standardverhalten, aber ich konnte es hier nicht gegen
 * eine echte Tauri-Instanz testen. Falls ein Aufruf mit einer Fehlermeldung
 * wie "missing required key `entry_id`" fehlschlaegt: einfach den
 * betroffenen Schluessel unten von camelCase auf snake_case umstellen
 * (z.B. `entryId` -> `entry_id`) - lokal, isolierter Fix, keine
 * Kettenreaktion auf andere Aufrufe.
 *
 * `invoke()` gibt ohne explizites Typ-Argument `Promise<unknown>` zurueck -
 * deshalb ueberall `invoke<T>(...)` mit explizitem Typ, sonst wuerde das
 * nicht gegen die unten deklarierten Rueckgabetypen kompilieren.
 */

import { invoke } from "@tauri-apps/api/core";

export interface ApiEntry {
  id: string;
  title: string;
  content: string;
  last_modified: string;
  manual_links: string[];
}

export interface ApiSearchResult {
  entry: ApiEntry;
  score: number;
}

export interface ApiLink {
  target_id: string;
  kind: "manual" | "suggested";
  score: number;
}

export interface ApiLanguageInfo {
  current: string;
  available: string[];
  snowball_available: boolean;
}

export const api = {
  async getAll(): Promise<ApiEntry[]> {
    return invoke<ApiEntry[]>("get_all_entries");
  },

  async recent(limit = 5): Promise<ApiEntry[]> {
    return invoke<ApiEntry[]>("get_recent", { limit });
  },

  async get(id: string): Promise<ApiEntry> {
    return invoke<ApiEntry>("get_entry", { id });
  },

  async search(query: string): Promise<ApiSearchResult[]> {
    return invoke<ApiSearchResult[]>("search_entries", { query });
  },

  async create(title: string, content: string): Promise<ApiEntry> {
    return invoke<ApiEntry>("create_entry", { title, content });
  },

  async update(id: string, title: string, content: string): Promise<ApiEntry> {
    return invoke<ApiEntry>("update_entry", { id, title, content });
  },

  async remove(id: string): Promise<void> {
    await invoke<void>("delete_entry", { id });
  },

  async linksFor(id: string): Promise<ApiLink[]> {
    return invoke<ApiLink[]>("get_links_for", { id });
  },

  async recordSelection(query: string, entryId: string): Promise<void> {
    await invoke<void>("record_selection", { query, entryId });
  },

  async addManualLink(entryId: string, targetId: string): Promise<void> {
    await invoke<void>("add_manual_link", { entryId, targetId });
  },

  async exportAll(): Promise<ApiEntry[]> {
    return invoke<ApiEntry[]>("export_all_entries");
  },

  async importEntries(entries: { title: string; content: string }[]): Promise<{ imported: number }> {
    const imported = await invoke<number>("import_entries", { entries });
    return { imported };
  },

  async deleteAll(): Promise<void> {
    await invoke<void>("delete_all_entries");
  },

  async getLanguage(): Promise<ApiLanguageInfo> {
    return invoke<ApiLanguageInfo>("get_language_info");
  },

  async setLanguage(lang: string): Promise<void> {
    await invoke<void>("set_language", { language: lang });
  },
};
