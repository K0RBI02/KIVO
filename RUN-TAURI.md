# KIVO als echte Desktop-App (Tauri) - Anleitung

**Ehrlicher Stand:** Ich hab dieses Grundgerüst geschrieben, aber NICHT
kompilieren koennen - meine Umgebung hat kein Rust/Cargo und keinen
Internetzugriff. Es folgt der offiziellen Tauri-2-API-Doku, aber beim
ersten Bauen bei dir koennen kleine Fehler auftauchen. Das ist normal -
schick mir einfach die Fehlermeldung, dann fixen wir sie zusammen.

## Was du einmalig installieren musst (auf deinem Windows-Rechner)

1. **Rust**: https://rustup.rs (Installer ausfuehren, Standardoptionen reichen)
2. **Visual Studio Build Tools** (C++ Workload) - Tauri braucht das zum
   Kompilieren unter Windows: https://visualstudio.microsoft.com/visual-cpp-build-tools/
3. **WebView2** - ist auf aktuellen Windows 10/11 meistens schon vorinstalliert,
   sonst: https://developer.microsoft.com/microsoft-edge/webview2/
4. Tauri-CLI:
   ```
   cargo install tauri-cli --version "^2"
   ```

## Bauen / Starten

```
cd src/frontend
cargo tauri dev
```

Das sollte automatisch:
- den Vite-Dev-Server starten (dein Frontend)
- den Python-Engine-Prozess im Hintergrund starten (`src/engine/webapp/server.py`)
- ein natives Fenster oeffnen

Fuer eine fertige, installierbare .exe:
```
cargo tauri build
```
Landet dann unter `src-tauri/target/release/bundle/`.

## Was noch fehlt, bevor du das an andere weitergeben kannst

1. **Python-Abhaengigkeit**: Aktuell muss auf dem Zielrechner Python 3
   installiert sein, weil main.rs `python3 webapp/server.py` startet.
   Fuer eine Version OHNE diese Voraussetzung: die Engine mit PyInstaller
   zu einer .exe buendeln (`pyinstaller --onefile webapp/server.py`) und
   das Ergebnis als Tauri-"Sidecar"-Binary registrieren statt `python3`
   direkt aufzurufen. Das ist ein separater Schritt, den wir angehen
   koennen, sobald die App bei dir grundsaetzlich laeuft.
2. **macOS-Icon** (`icon.icns`): hab ich nicht erzeugen koennen (braucht
   `iconutil`, nur auf macOS verfuegbar). Fuer Windows reicht `icon.ico`,
   das ist schon dabei.
3. Die `identifier` in `tauri.conf.json` (`com.kivo.app`) ist ein
   Platzhalter - fuer einen echten Store-Release solltest du das auf
   etwas Eindeutiges aendern.

## Wenn's beim ersten Start hakt

Häufigste Stolpersteine bei einem frisch generierten Tauri-Projekt:
- Fehlende Build Tools (siehe oben) -> Fehlermeldung erwaehnt meist "link.exe" o.ae.
- Tauri-Version in `Cargo.toml` passt nicht exakt zur installierten CLI-Version
  -> `cargo tauri --version` pruefen, ggf. Cargo.toml-Version anpassen
