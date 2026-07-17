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

export interface ApiLanguageInfo {
  current: string;
  available: string[];
  snowball_available: boolean;
}

export class KivoApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "KivoApiError";
    this.status = status;
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch {
    throw new KivoApiError("KIVO Engine nicht erreichbar. Läuft der lokale Server?");
  }

  if (!res.ok) {
    let message = `KIVO API Fehler (${res.status})`;
    try {
      const body = await res.json();
      if (body?.error) message = body.error;
    } catch {
      // Antwort war kein JSON - Standardmeldung behalten
    }
    throw new KivoApiError(message, res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getAll(): Promise<ApiEntry[]> {
    return request(`${API_BASE}/api/entries`);
  },

  async recent(limit = 5): Promise<ApiEntry[]> {
    return request(`${API_BASE}/api/recent?limit=${limit}`);
  },

  async get(id: string): Promise<ApiEntry> {
    return request(`${API_BASE}/api/entries/${id}`);
  },

  async search(query: string): Promise<ApiSearchResult[]> {
    return request(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
  },

  async create(title: string, content: string): Promise<ApiEntry> {
    return request(`${API_BASE}/api/entries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
  },

  async update(id: string, title: string, content: string): Promise<ApiEntry> {
    return request(`${API_BASE}/api/entries/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
  },

  async remove(id: string): Promise<void> {
    await request(`${API_BASE}/api/entries/${id}`, { method: "DELETE" });
  },

  async linksFor(id: string): Promise<ApiLink[]> {
    return request(`${API_BASE}/api/entries/${id}/links`);
  },

  async recordSelection(query: string, entryId: string): Promise<void> {
    await request(`${API_BASE}/api/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, entry_id: entryId }),
    });
  },

  async addManualLink(entryId: string, targetId: string): Promise<void> {
    await request(`${API_BASE}/api/link/${entryId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_id: targetId }),
    });
  },

  async exportAll(): Promise<ApiEntry[]> {
    return request(`${API_BASE}/api/export`);
  },

  async importEntries(entries: { title: string; content: string }[]): Promise<{ imported: number }> {
    return request(`${API_BASE}/api/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entries }),
    });
  },

  async deleteAll(): Promise<void> {
    await request(`${API_BASE}/api/entries`, { method: "DELETE" });
  },

  async getLanguage(): Promise<ApiLanguageInfo> {
    return request(`${API_BASE}/api/language`);
  },

  async setLanguage(lang: string): Promise<void> {
    await request(`${API_BASE}/api/language`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: lang }),
    });
  },
};