use serde::{Deserialize, Serialize};
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

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
enum Color {
    Named(String),
    Rgb([u8; 3]),
    Rgba([u8; 4]),
}

impl Default for Color {
    fn default() -> Self {
        Self::Rgb([0, 0, 0])
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Layout {
    #[serde(rename = "grid-size")]
    grid_size: (i32, i32),

    // Allows either a single number or a tuple [x, y] in TOML.
    gap: toml::Value,

    // Allows number | [x, y] | [t, r, b, l] in TOML.
    margin: toml::Value,
}

impl Default for Layout {
    fn default() -> Self {
        Self {
            grid_size: (1, 1),
            gap: toml::Value::Float(0.0),
            margin: toml::Value::Float(0.0),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct TextSpec {
    template: String,
    position: (f64, f64),
    ttf: Option<String>,
    #[serde(default = "default_text_size")]
    size: i32,
    #[serde(default)]
    color: Color,
}

fn default_text_size() -> i32 {
    16
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct OutputSpec {
    #[serde(rename = "background-color", default = "default_background_color")]
    background_color: Color,
}

fn default_background_color() -> Color {
    Color::Named("white".to_string())
}

impl Default for OutputSpec {
    fn default() -> Self {
        Self {
            background_color: default_background_color(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct StampSpec {
    #[serde(rename = "stack-size", default = "default_stack_size")]
    stack_size: i32,

    #[serde(rename = "source-image", default)]
    source_image: String,

    #[serde(default)]
    layout: Layout,

    #[serde(default)]
    texts: Vec<TextSpec>,

    #[serde(default)]
    output: OutputSpec,

    #[serde(default = "default_background")]
    background: Color,
    // We deliberately ignore/omit advanced fields for V1.
}

fn default_stack_size() -> i32 {
    1
}

fn default_background() -> Color {
    Color::Rgb([255, 255, 255])
}

impl StampSpec {
    fn normalize_for_save(mut self) -> Self {
        if self.stack_size < 1 {
            self.stack_size = 1;
        }
        if self.layout.grid_size.0 < 1 {
            self.layout.grid_size.0 = 1;
        }
        if self.layout.grid_size.1 < 1 {
            self.layout.grid_size.1 = 1;
        }

        // Ensure there is at least one text entry to match current UX expectations.
        if self.texts.is_empty() {
            self.texts.push(TextSpec {
                template: "Sample Text".to_string(),
                position: (10.0, 10.0),
                ttf: None,
                size: 24,
                color: Color::Named("black".to_string()),
            });
        }

        self
    }

    fn to_canonical_toml_string(self) -> Result<String, String> {
        toml::to_string_pretty(&self.normalize_for_save())
            .map_err(|e| format!("Failed to serialize spec to TOML: {e}"))
    }
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

fn read_spec_toml(workspace_dir: &Path) -> Result<String, String> {
    let spec_path = spec_path_for(workspace_dir);
    if !spec_path.exists() {
        return Ok(DEFAULT_SPEC_TOML.to_string());
    }
    fs::read_to_string(&spec_path).map_err(|e| format!("Failed to read spec.toml: {e}"))
}

fn parse_spec_from_toml(toml_text: &str) -> Result<StampSpec, String> {
    toml::from_str::<StampSpec>(toml_text).map_err(|e| format!("Invalid spec.toml: {e}"))
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
fn workspace_get_spec_json(workspace_id: String) -> Result<StampSpec, String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let toml_text = read_spec_toml(&workspace_dir)?;
    let parsed = parse_spec_from_toml(&toml_text).unwrap_or_else(|_| {
        // If the existing TOML is invalid, fall back to defaults rather than crashing the UI.
        StampSpec {
            stack_size: default_stack_size(),
            source_image: "".to_string(),
            layout: Layout::default(),
            texts: vec![TextSpec {
                template: "Sample Text".to_string(),
                position: (10.0, 10.0),
                ttf: None,
                size: 24,
                color: Color::Named("black".to_string()),
            }],
            output: OutputSpec::default(),
            background: default_background(),
        }
    });

    Ok(parsed)
}

#[tauri::command]
fn workspace_set_spec_json(workspace_id: String, spec: StampSpec) -> Result<(), String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    ensure_workspace_layout(&workspace_dir)?;
    let spec_path = spec_path_for(&workspace_dir);

    let toml_out = spec.to_canonical_toml_string()?;
    fs::write(&spec_path, toml_out).map_err(|e| format!("Failed to write spec.toml: {e}"))
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
            workspace_get_spec_json,
            workspace_set_spec_json
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
