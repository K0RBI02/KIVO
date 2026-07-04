/**
 * KIVO API Client
 *
 * Bewusst duenn: kein Suchen, Ranken, Sortieren, keine Empfehlungen hier.
 * Nur JSON hin- und herschicken. Die gesamte Logik lebt in der Python-Engine
 * (siehe kivo/src/search/engine.py), die lokal unter API_BASE laeuft:
 *
 *     cd kivo/src && python3 webapp/server.py
 */

const API_BASE = "http://127.0.0.1:8420";

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

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`KIVO API error: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getAll(): Promise<ApiEntry[]> {
    return json(await fetch(`${API_BASE}/api/entries`));
  },

  async recent(limit = 5): Promise<ApiEntry[]> {
    return json(await fetch(`${API_BASE}/api/recent?limit=${limit}`));
  },

  async get(id: string): Promise<ApiEntry> {
    return json(await fetch(`${API_BASE}/api/entries/${id}`));
  },

  async search(query: string): Promise<ApiSearchResult[]> {
    return json(await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`));
  },

  async create(title: string, content: string): Promise<ApiEntry> {
    return json(
      await fetch(`${API_BASE}/api/entries`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      })
    );
  },

  async update(id: string, title: string, content: string): Promise<ApiEntry> {
    return json(
      await fetch(`${API_BASE}/api/entries/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      })
    );
  },

  async remove(id: string): Promise<void> {
    await fetch(`${API_BASE}/api/entries/${id}`, { method: "DELETE" });
  },

  async linksFor(id: string): Promise<ApiLink[]> {
    return json(await fetch(`${API_BASE}/api/entries/${id}/links`));
  },

  async recordSelection(query: string, entryId: string): Promise<void> {
    await fetch(`${API_BASE}/api/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, entry_id: entryId }),
    });
  },
};
