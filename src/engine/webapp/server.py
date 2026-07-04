"""
KIVO Search Engine
Lokaler HTTP-API-Server

Bewusst reines stdlib (http.server), kein pip install noetig.
Das ist EIN Client der Engine (naemlich der HTTP-API-Client) -
enthaelt selbst KEINE Such-/Rank-Logik, nur Ver-/Entpacken von JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote
from uuid import UUID

# Robust gegen unterschiedliche Startarten (python webapp/server.py ODER
# python -m webapp.server) - src/ muss immer auf dem Pfad sein.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from search.engine import KnowledgeEngine

engine = KnowledgeEngine(data_dir="kivo_data")


def entry_to_json(entry) -> dict:
    return {
        "id": str(entry.id),
        "title": entry.title,
        "content": entry.content,
        "last_modified": entry.last_modified.isoformat(),
        "manual_links": [str(l.target_id) for l in entry.manual_links],
    }


class Handler(BaseHTTPRequestHandler):

    def _send_json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self) -> None:
        self._send_json({})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = parse_qs(parsed.query)

        if parts == ["api", "entries"]:
            self._send_json([entry_to_json(e) for e in engine.get_all()])
            return

        if len(parts) == 3 and parts[:2] == ["api", "entries"]:
            entry = engine.get(UUID(parts[2]))
            if entry is None:
                self._send_json({"error": "not found"}, 404)
                return
            self._send_json(entry_to_json(entry))
            return

        if len(parts) == 4 and parts[:2] == ["api", "entries"] and parts[3] == "links":
            entry_id = UUID(parts[2])
            links = engine.links_for(entry_id)
            self._send_json([
                {"target_id": str(l.target_id), "kind": l.kind, "score": l.score}
                for l in links
            ])
            return

        if parts == ["api", "recent"]:
            limit = int(query.get("limit", ["5"])[0])
            self._send_json([entry_to_json(e) for e in engine.recent(limit)])
            return

        if parts == ["api", "search"]:
            q = unquote(query.get("q", [""])[0])
            results = engine.search(q)
            self._send_json([
                {"entry": entry_to_json(r.entry), "score": r.score}
                for r in results
            ])
            return

        self._send_json({"error": "unknown route"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        data = self._read_json()

        if parts == ["api", "entries"]:
            entry = engine.create(data.get("title", ""), data.get("content", ""))
            self._send_json(entry_to_json(entry), 201)
            return

        if len(parts) == 3 and parts[:2] == ["api", "entries"]:
            entry = engine.update(UUID(parts[2]), title=data.get("title"), content=data.get("content"))
            if entry is None:
                self._send_json({"error": "not found"}, 404)
                return
            self._send_json(entry_to_json(entry))
            return

        if parts == ["api", "select"]:
            engine.record_selection(data.get("query", ""), UUID(data["entry_id"]))
            self._send_json({"ok": True})
            return

        if len(parts) == 3 and parts[:2] == ["api", "link"]:
            engine.link(UUID(parts[2]), UUID(data["target_id"]))
            self._send_json({"ok": True})
            return

        self._send_json({"error": "unknown route"}, 404)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        if len(parts) == 3 and parts[:2] == ["api", "entries"]:
            engine.delete(UUID(parts[2]))
            self._send_json({"ok": True})
            return

        self._send_json({"error": "unknown route"}, 404)

    def log_message(self, format, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def main(port: int = 8420) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"KIVO API laeuft auf http://127.0.0.1:{port}")
    print("Endpunkte: GET /api/search?q=..., GET/POST /api/entries, GET /api/entries/<id>/links")
    server.serve_forever()


if __name__ == "__main__":
    main()
