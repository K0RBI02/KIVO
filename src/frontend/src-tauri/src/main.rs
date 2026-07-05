// KIVO Desktop (Tauri)
//
// UNVERIFIZIERT: ich konnte das hier nicht kompilieren (keine Rust-Toolchain
// in meiner Umgebung). Der Code folgt der dokumentierten Tauri-2-API nach
// bestem Wissen, aber beim ersten `cargo tauri dev` bei dir koennen noch
// kleine Anpassungen noetig sein - meld dich, dann fixen wir das zusammen.
//
// Was das hier tut: startet automatisch den Python-Engine-Prozess
// (src/engine/webapp/server.py) im Hintergrund, wenn die App aufgeht,
// und beendet ihn wieder, wenn die App geschlossen wird - damit du nicht
// mehr manuell zwei Terminals offen halten musst.
//
// WICHTIG fuer eine "richtige", verteilbare App (z.B. an andere Leute
// weitergeben): dieser Ansatz setzt voraus, dass Python auf dem Zielrechner
// installiert ist. Fuer eine Version ohne Python-Abhaengigkeit muesste die
// Engine mit PyInstaller zu einer eigenstaendigen .exe gebaut und als
// Tauri-"Sidecar"-Binary eingebunden werden - das ist ein separater,
// noch offener Schritt.

use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;

struct EnginePocess(Mutex<Option<Child>>);

fn spawn_engine() -> Option<Child> {
    // Pfad relativ zu src-tauri/ - passt zur aktuellen Projektstruktur
    // (src/frontend/src-tauri -> ../../engine/webapp/server.py)
    let engine_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("engine");

    // Probiert mehrere uebliche Namen der Reihe nach, statt fest an einen
    // bestimmten Rechner/Nutzernamen gebunden zu sein (portabel).
    let candidates: &[&str] = if cfg!(windows) {
        &["python", "python3", "py"]
    } else {
        &["python3", "python"]
    };

    for candidate in candidates {
        let result = Command::new(candidate)
            .arg("webapp/server.py")
            .current_dir(&engine_dir)
            .spawn();

        if let Ok(child) = result {
            return Some(child);
        }
    }

    eprintln!(
        "[KIVO] Engine konnte nicht gestartet werden - keiner von {:?} im PATH gefunden.",
        candidates
    );
    None
}

fn main() {
    tauri::Builder::default()
        .manage(EnginePocess(Mutex::new(spawn_engine())))
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Ok(mut guard) = window.state::<EnginePocess>().0.lock() {
                    if let Some(child) = guard.as_mut() {
                        let _ = child.kill();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running KIVO");
}
