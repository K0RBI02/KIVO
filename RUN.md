# KIVO starten

Ein Prozess, ein Terminal. Kein Python, kein separater Server mehr –
die gesamte Suchlogik läuft nativ im Rust-Backend.

## Einmalig einrichten

1. **Rust**: https://rustup.rs (Installer ausführen, Standardoptionen reichen)
2. **Tauri-CLI**:
   ```
   cargo install tauri-cli --version "^2"
   ```
3. Plattformspezifisch:
   - **Windows**: Visual Studio Build Tools (C++ Workload) –
     https://visualstudio.microsoft.com/visual-cpp-build-tools/,
     WebView2 ist auf aktuellen Windows 10/11 meist schon vorinstalliert
     (sonst: https://developer.microsoft.com/microsoft-edge/webview2/)
   - **Linux (Fedora)**: `webkit2gtk`, `gtk3` und Build-Tools werden beim
     ersten `cargo build` über die Systempaketverwaltung mitgezogen bzw.
     müssen vorher installiert sein (siehe Tauri-Doku für deine Distro)
   - **macOS**: Xcode Command Line Tools (`xcode-select --install`)
4. Node-Abhängigkeiten installieren (im Repo-Root):
   ```
   npm install
   ```

## Starten (Entwicklung)

Im Repo-Root:
```
cargo tauri dev
```

Das startet automatisch:
- den Vite-Dev-Server (Frontend, Hot Reload)
- den Rust-Build im Hintergrund
- ein natives Fenster

## Bauen (fertige, installierbare App)

```
cargo tauri build
```

Ergebnis liegt unter `src-tauri/target/release/bundle/` (`.deb`/`.rpm` auf
Linux, `.msi`/NSIS-Setup auf Windows, `.app`/`.dmg` auf macOS).

**Bekanntes Problem auf manchen Linux-Systemen (u. a. Fedora):** Der
AppImage-Bundling-Schritt kann mit `failed to run linuxdeploy`
fehlschlagen (fehlendes `libfuse.so.2`). `.deb`/`.rpm` werden davon nicht
beeinträchtigt – sie sind zu diesem Zeitpunkt schon fertig gebaut. Falls
der Fehler stört, `"targets": "all"` in `src-tauri/tauri.conf.json` auf
`["deb", "rpm"]` einschränken, dann wird AppImage gar nicht erst versucht.

## Wo deine Daten liegen

Kein `kivo_data`-Ordner mehr im Projektverzeichnis – die App nutzt das
offizielle, plattformspezifische App-Datenverzeichnis:

- **Linux**: `~/.local/share/com.kivo.app/kivo_data/entries.json`
- **Windows**: `%APPDATA%\com.kivo.app\kivo_data\entries.json`
- **macOS**: `~/Library/Application Support/com.kivo.app/kivo_data/entries.json`

## Was du ausprobieren kannst

- Neue Notiz anlegen (Stift-Icon unten rechts oder ⌘/Strg+N)
- Nach einem Wort suchen, das NICHT im Titel steht, nur im Inhalt
- Absichtlich unscharf/falsch tippen (Fuzzy-Matching)
- Zwei Notizen mit gemeinsamem Begriff anlegen (z. B. "Docker" in beiden),
  eine davon öffnen → unten bei "Related" taucht die andere automatisch
  als Vorschlag auf, ganz ohne manuelles Verlinken
- Eine Tabelle mit `^` hinter einem Spaltennamen schreiben (z. B.
  `Prio^`) → wird in der Ansicht automatisch sortiert
- `[ ]` / `[x]` in einer Tabellenzelle → wird als Checkbox angezeigt
- Sprache in den Settings umschalten (auto/de/en)
- App komplett schließen und neu starten → Notizen sind noch da