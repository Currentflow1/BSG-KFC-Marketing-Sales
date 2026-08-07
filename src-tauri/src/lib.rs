use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      let sidecar = app.shell().sidecar("django-backend")?;
      let (mut rx, _child) = sidecar.spawn().expect("failed to spawn django-backend sidecar");

      tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
          match event {
            CommandEvent::Stdout(line) => {
              println!("[django] {}", String::from_utf8_lossy(&line));
            }
            CommandEvent::Stderr(line) => {
              eprintln!("[django-err] {}", String::from_utf8_lossy(&line));
            }
            _ => {}
          }
        }
      });

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}