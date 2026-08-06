// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri_plugin_shell::ShellExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let shell = app.shell();
            let sidecar = shell
                .sidecar("django-backend")
                .expect("failed to create django-backend sidecar command");

            let (mut _rx, _child) = sidecar.spawn().expect("failed to spawn django-backend");

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}