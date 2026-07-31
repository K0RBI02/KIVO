// KIVO Desktop (Tauri)
//
// WICHTIGER STAND: ab hier laeuft KIVO komplett nativ - kein Python-
// Subprozess mehr, kein lokaler HTTP-Server, kein GET/POST. Die komplette
// Such-Engine ist als Rust-Code im `engine`-Modul portiert und wird ueber
// Tauri-Commands (`commands`-Modul) direkt vom Frontend per `invoke()`
// angesprochen.
//
// UNVERIFIZIERT: dieses main.rs konnte ich (wie schon die vorherigen
// main.rs-Versionen in diesem Projekt) nicht selbst kompilieren - keine
// Rust-Toolchain und kein Internetzugriff in meiner Umgebung, um die
// exakte Tauri-v2-API (insbesondere `app.path().app_data_dir()` und
// `App::manage()`) gegenzupruefen. Das ist der Teil mit dem groessten
// Unsicherheitsfaktor im gesamten Rust-Port bisher, weil er von der
// Tauri-Framework-API abhaengt statt von stabilen, weit verbreiteten
// Crates wie serde/uuid/chrono. Bei `cargo check`-Fehlern hier bitte die
// Fehlermeldung schicken, dann fixen wir das gezielt.
//
// DATENVERZEICHNIS: nutzt bewusst das offizielle, plattformspezifische
// App-Datenverzeichnis (z.B. unter Windows `%APPDATA%\com.kivo.app\`,
// unter Linux `~/.local/share/com.kivo.app/`) statt eines relativen
// "kivo_data"-Pfads. Grund: bei einer ECHTEN installierten App (.rpm/.exe,
// nicht `cargo tauri dev`) ist das Arbeitsverzeichnis beim Start durch
// Doppelklick/Startmenue NICHT verlaesslich der Projektordner - ein
// relativer Pfad haette dort schlicht nicht zuverlaessig funktioniert.
//
// EINMALIGER MIGRATIONSSCHRITT NOETIG: deine bisherigen Test-Eintraege
// liegen noch unter `src/engine/kivo_data/entries.json` (dort, wo der
// Python-Server sie abgelegt hat). Die neue native Version sucht an einem
// anderen, plattformabhaengigen Ort. Um deine bisherigen Eintraege zu
// behalten, einmalig `entries.json` dorthin kopieren:
//   Windows:  %APPDATA%\com.kivo.app\kivo_data\entries.json
//   Linux:    ~/.local/share/com.kivo.app/kivo_data/entries.json
//   macOS:    ~/Library/Application Support/com.kivo.app/kivo_data/entries.json
// (Ordner ggf. manuell anlegen, falls er beim ersten Start noch nicht
// existiert - je nachdem, ob KIVO vorher schon einmal nativ gestartet
// wurde.)

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;

use tauri::Manager;

mod commands;
mod engine;

use engine::engine::KnowledgeEngine;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("App-Datenverzeichnis sollte auf allen unterstuetzten Plattformen verfuegbar sein")
                .join("kivo_data");

            let knowledge_engine = KnowledgeEngine::new(&data_dir, true, "auto")
                .expect("KnowledgeEngine konnte nicht initialisiert werden (Datenverzeichnis nicht beschreibbar?)");

            app.manage(Mutex::new(knowledge_engine));

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_all_entries,
            commands::get_recent,
            commands::get_entry,
            commands::search_entries,
            commands::create_entry,
            commands::update_entry,
            commands::delete_entry,
            commands::get_links_for,
            commands::record_selection,
            commands::add_manual_link,
            commands::export_all_entries,
            commands::import_entries,
            commands::delete_all_entries,
            commands::get_language_info,
            commands::set_language,
        ])
        .run(tauri::generate_context!())
        .expect("error while running KIVO");
}
