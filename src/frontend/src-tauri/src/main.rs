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
    let engine_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("engine");

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

        let mut child = match result {
            Ok(child) => child,
            Err(_) => continue,
        };

        // Kurzer Health-Check: sofortiger Crash (Port belegt,
        // fehlendes Modul, ...) soll nicht als Erfolg durchgehen.
        std::thread::sleep(std::time::Duration::from_millis(400));

        match child.try_wait() {
            Ok(Some(status)) => {
                eprintln!(
                    "[KIVO] '{candidate}' ist sofort beendet (status: {status:?}) - versuche naechsten Kandidaten."
                );
                continue;
            }
            Ok(None) => return Some(child), // laeuft noch -> gutes Zeichen
            Err(err) => {
                eprintln!("[KIVO] Konnte Engine-Status nicht pruefen: {err}");
                return Some(child);
            }
        }
    }

    eprintln!(
        "[KIVO] Engine konnte nicht gestartet werden - keiner von {candidates:?} im PATH gefunden oder alle sofort abgestuerzt."
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
