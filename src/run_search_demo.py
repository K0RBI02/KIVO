"""
KIVO Search Engine - Demo

Rekonstruiert genau die Beispiele aus deiner Spec:
  Notizen: Caddy Installation, Docker Commands, Fedora Befehle,
           Proxy Konfigurationen, Linux Tricks
  Suchen:  "Wie hieß dieses Proxy-Dings?"
           "Ich hatte mal Caddy auf Fedora installiert."
           "Was weiß ich über Docker?"
"""

from search.engine import KnowledgeEngine

engine = KnowledgeEngine()

engine.create(
    "Caddy Installation",
    "Caddy auf Fedora installieren. sudo dnf install caddy. "
    "Danach den Reverse Proxy in der Caddyfile konfigurieren.",
)
engine.create(
    "Docker Commands",
    "Wichtige Docker Befehle: docker ps, docker compose up -d, "
    "docker network ls. Docker Compose fuer Multi-Container Setups.",
)
engine.create(
    "Fedora Befehle",
    "Fedora nutzt dnf statt apt. dnf install, dnf update, "
    "systemctl fuer Services. Firewall mit firewall-cmd.",
)
engine.create(
    "Proxy Konfigurationen",
    "Reverse Proxy Konfiguration mit Caddy oder Nginx. "
    "Automatisches HTTPS ueber Let's Encrypt bei Caddy.",
)
engine.create(
    "Linux Tricks",
    "Nuetzliche Linux Kommandos: grep, awk, sed, journalctl "
    "fuer Logs, systemctl status fuer Services.",
)

queries = [
    "Wie hieß dieses Proxy-Dings?",
    "Ich hatte mal Caddy auf Fedora installiert",
    "Was weiß ich über Docker?",
    "Wo war nochmal der Reverse Proxy",
]

for q in queries:
    print(f"\n=== Suche: \"{q}\" ===")
    results = engine.search(q)
    if not results:
        print("  (keine Treffer)")
    for r in results:
        print(f"  {r.score:5.2f}  {r.entry.title}")

# Discovery-Beweis: welche Begriffe hat die Engine SELBST als Konzepte erkannt?
print("\n=== Selbst entdeckte Konzepte (kein eingebautes Wissen!) ===")
concepts = sorted(
    (c for c in engine.analysis.concepts.values() if c.is_concept),
    key=lambda c: c.document_frequency,
    reverse=True,
)
for c in concepts:
    print(f"  {c.term:15s}  in {c.document_frequency} Entries, {c.total_frequency}x total")

# Link-Vorschlaege fuer "Caddy Installation" - der Nutzer sieht den Graphen nie,
# nur diese fertigen Vorschlaege
print("\n=== Link-Vorschlaege fuer 'Caddy Installation' ===")
caddy_entry = next(e for e in engine.get_all() if e.title == "Caddy Installation")
links = engine.links_for(caddy_entry.id)
for link in links:
    target = engine.get(link.target_id)
    marker = "manuell" if link.kind == "manual" else f"vorschlag (score={link.score:.1f})"
    print(f"  -> {target.title}  [{marker}]")
