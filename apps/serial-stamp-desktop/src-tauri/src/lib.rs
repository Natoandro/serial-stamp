use serde::Serialize;
use std::{
    collections::HashMap,
    fs,
    path::{Path, PathBuf},
    sync::{Mutex, OnceLock},
};
use tauri::Manager;

const DEFAULT_SPEC_TOML: &str = r#"stack-size = 1
source-image = ""

[layout]
grid-size = [1, 1]
gap = 0
margin = 0

[[texts]]
template = "Sample Text"
position = [10, 10]
size = 24
color = "black"
"#;

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct WorkspaceInfo {
    workspace_id: String,
    workspace_dir: String,
}

#[derive(Default)]
struct WorkspaceState {
    workspaces: HashMap<String, PathBuf>,
}

static WORKSPACES: OnceLock<Mutex<WorkspaceState>> = OnceLock::new();

fn workspaces() -> &'static Mutex<WorkspaceState> {
    WORKSPACES.get_or_init(|| Mutex::new(WorkspaceState::default()))
}

fn spec_path_for(workspace_dir: &Path) -> PathBuf {
    workspace_dir.join("spec.toml")
}

fn ensure_workspace_layout(workspace_dir: &Path) -> Result<(), String> {
    fs::create_dir_all(workspace_dir.join("assets"))
        .map_err(|e| format!("Failed to create workspace assets dir: {e}"))?;

    let spec_path = spec_path_for(workspace_dir);
    if !spec_path.exists() {
        fs::write(&spec_path, DEFAULT_SPEC_TOML)
            .map_err(|e| format!("Failed to write default spec.toml: {e}"))?;
    }

    Ok(())
}

#[tauri::command]
fn workspace_new(app: tauri::AppHandle) -> Result<WorkspaceInfo, String> {
    let workspace_id = uuid::Uuid::new_v4().to_string();

    let base_dir = app
        .path()
        .temp_dir()
        .map_err(|e| format!("Failed to resolve temp dir: {e}"))?
        .join("serial-stamp-workspaces")
        .join(&workspace_id);

    ensure_workspace_layout(&base_dir)?;

    {
        let mut state = workspaces()
            .lock()
            .map_err(|_| "Workspace state lock poisoned".to_string())?;
        state
            .workspaces
            .insert(workspace_id.clone(), base_dir.clone());
    }

    Ok(WorkspaceInfo {
        workspace_id,
        workspace_dir: base_dir.to_string_lossy().to_string(),
    })
}

fn get_workspace_dir(workspace_id: &str) -> Result<PathBuf, String> {
    let state = workspaces()
        .lock()
        .map_err(|_| "Workspace state lock poisoned".to_string())?;

    state
        .workspaces
        .get(workspace_id)
        .cloned()
        .ok_or_else(|| format!("Unknown workspace_id: {workspace_id}"))
}

#[tauri::command]
fn workspace_get_spec(workspace_id: String) -> Result<String, String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let spec_path = spec_path_for(&workspace_dir);

    if !spec_path.exists() {
        return Ok(DEFAULT_SPEC_TOML.to_string());
    }

    fs::read_to_string(&spec_path).map_err(|e| format!("Failed to read spec.toml: {e}"))
}

#[tauri::command]
fn workspace_set_spec(workspace_id: String, spec_toml: String) -> Result<(), String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    ensure_workspace_layout(&workspace_dir)?;
    let spec_path = spec_path_for(&workspace_dir);

    fs::write(&spec_path, spec_toml).map_err(|e| format!("Failed to write spec.toml: {e}"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            workspace_new,
            workspace_get_spec,
            workspace_set_spec
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
