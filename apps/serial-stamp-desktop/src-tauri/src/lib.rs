use base64::Engine;
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs,
    io::{Read, Write},
    path::{Path, PathBuf},
    process::Command,
    sync::{Mutex, OnceLock},
};
use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    AppHandle, Emitter, Manager,
};
use walkdir::WalkDir;
use zip::write::FileOptions;

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

fn emit_menu_action(app: &AppHandle, menu_id: &str) {
    // Only emit for our custom menu items (ignore predefined items like quit).
    match menu_id {
        "project.new" | "project.open" | "project.save" | "project.save_as" | "export.pdf" => {
            // Frontend should listen to `menu://action` and branch on the `id`.
            let _ = app.emit("menu://action", menu_id.to_string());
        }
        _ => {}
    }
}

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
    #[serde(skip_serializing_if = "Option::is_none")]
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
    fs::create_dir_all(workspace_dir.join("images"))
        .map_err(|e| format!("Failed to create workspace images dir: {e}"))?;
    fs::create_dir_all(workspace_dir.join("fonts"))
        .map_err(|e| format!("Failed to create workspace fonts dir: {e}"))?;

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

fn pack_workspace(workspace_dir: &Path, dest_zip_path: &Path) -> Result<(), String> {
    let file =
        fs::File::create(dest_zip_path).map_err(|e| format!("Failed to create zip file: {e}"))?;
    let mut zip = zip::ZipWriter::new(file);
    let options = FileOptions::default()
        .compression_method(zip::CompressionMethod::Stored)
        .unix_permissions(0o755);

    // 1. Add spec.toml
    let spec_path = workspace_dir.join("spec.toml");
    if spec_path.exists() {
        zip.start_file("spec.toml", options)
            .map_err(|e| format!("Zip error: {e}"))?;
        let mut f =
            fs::File::open(&spec_path).map_err(|e| format!("Failed to open spec.toml: {e}"))?;
        let mut buffer = Vec::new();
        f.read_to_end(&mut buffer)
            .map_err(|e| format!("Failed to read spec.toml: {e}"))?;
        zip.write_all(&buffer)
            .map_err(|e| format!("Failed to write spec.toml to zip: {e}"))?;
    }

    // 2. Add resources recursively
    for folder in ["images", "fonts"] {
        let dir = workspace_dir.join(folder);
        if dir.exists() {
            for entry in WalkDir::new(&dir) {
                let entry = entry.map_err(|e| format!("WalkDir error: {e}"))?;
                let path = entry.path();
                if path.is_file() {
                    let name = path
                        .strip_prefix(workspace_dir)
                        .map_err(|e| format!("Path prefix error: {e}"))?
                        .to_str()
                        .ok_or("Invalid path encoding")?;

                    // On Windows, paths might use backslashes, but zip expects forward slashes.
                    #[cfg(windows)]
                    let name = name.replace('\\', "/");

                    zip.start_file(name, options)
                        .map_err(|e| format!("Zip error for {name}: {e}"))?;
                    let mut f = fs::File::open(path)
                        .map_err(|e| format!("Failed to open file {path:?}: {e}"))?;
                    let mut buffer = Vec::new();
                    f.read_to_end(&mut buffer)
                        .map_err(|e| format!("Failed to read file {path:?}: {e}"))?;
                    zip.write_all(&buffer)
                        .map_err(|e| format!("Failed to write file {path:?} to zip: {e}"))?;
                }
            }
        }
    }

    zip.finish()
        .map_err(|e| format!("Failed to finish zip: {e}"))?;
    Ok(())
}

fn unpack_stamp(app: &AppHandle, stamp_path: &Path) -> Result<WorkspaceInfo, String> {
    let file = fs::File::open(stamp_path).map_err(|e| format!("Failed to open stamp file: {e}"))?;
    let mut archive =
        zip::ZipArchive::new(file).map_err(|e| format!("Failed to read zip archive: {e}"))?;

    // Create new workspace
    let workspace_info = workspace_new(app.clone())?;
    let workspace_dir = PathBuf::from(&workspace_info.workspace_dir);

    for i in 0..archive.len() {
        let mut file = archive
            .by_index(i)
            .map_err(|e| format!("Zip error at index {i}: {e}"))?;

        let outpath = match file.enclosed_name() {
            Some(path) => workspace_dir.join(path),
            None => continue,
        };

        if file.name().ends_with('/') {
            fs::create_dir_all(&outpath)
                .map_err(|e| format!("Failed to create dir {outpath:?}: {e}"))?;
        } else {
            if let Some(p) = outpath.parent() {
                if !p.exists() {
                    fs::create_dir_all(p)
                        .map_err(|e| format!("Failed to create dir {p:?}: {e}"))?;
                }
            }
            let mut outfile = fs::File::create(&outpath)
                .map_err(|e| format!("Failed to create file {outpath:?}: {e}"))?;
            std::io::copy(&mut file, &mut outfile)
                .map_err(|e| format!("Failed to extract file {outpath:?}: {e}"))?;
        }
    }

    Ok(workspace_info)
}

#[tauri::command]
fn workspace_add_file(
    workspace_id: String,
    src_path: String,
    category: String,
) -> Result<String, String> {
    if category != "images" && category != "fonts" {
        return Err("Invalid category. Must be 'images' or 'fonts'".to_string());
    }
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let src = PathBuf::from(&src_path);
    let filename = src
        .file_name()
        .ok_or("Invalid source path")?
        .to_string_lossy()
        .to_string();

    let dest_dir = workspace_dir.join(&category);
    fs::create_dir_all(&dest_dir).map_err(|e| format!("Failed to create dir: {e}"))?;

    let dest = dest_dir.join(&filename);
    fs::copy(&src, &dest).map_err(|e| format!("Failed to copy file: {e}"))?;

    // Return relative path like "images/foo.png" or "fonts/bar.ttf"
    Ok(format!("{}/{}", category, filename))
}

#[tauri::command]
fn workspace_list_files(workspace_id: String, category: String) -> Result<Vec<String>, String> {
    if category != "images" && category != "fonts" {
        return Err("Invalid category. Must be 'images' or 'fonts'".to_string());
    }
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let target_dir = workspace_dir.join(&category);

    let mut files = Vec::new();
    if target_dir.exists() {
        for entry in fs::read_dir(target_dir).map_err(|e| format!("Read dir error: {e}"))? {
            let entry = entry.map_err(|e| format!("Entry error: {e}"))?;
            let path = entry.path();
            if path.is_file() {
                if let Some(name) = path.file_name() {
                    files.push(format!("{}/{}", category, name.to_string_lossy()));
                }
            }
        }
    }
    files.sort();
    Ok(files)
}

#[tauri::command]
fn workspace_remove_file(
    workspace_id: String,
    category: String,
    filename: String,
) -> Result<(), String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    if filename.contains("..") {
        return Err("Invalid filename".to_string());
    }
    let path = workspace_dir.join(&filename);

    // Check if path is inside workspace_dir/category
    let cat_dir = workspace_dir.join(&category);
    if !path.starts_with(&cat_dir) {
        return Err("Invalid file path".to_string());
    }

    if path.exists() {
        fs::remove_file(path).map_err(|e| format!("Failed to remove file: {e}"))?;
    }
    Ok(())
}

#[tauri::command]
fn project_pack(workspace_id: String, dest_path: String) -> Result<(), String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let dest_path = PathBuf::from(dest_path);
    pack_workspace(&workspace_dir, &dest_path)
}

#[tauri::command]
fn project_unpack(app: tauri::AppHandle, file_path: String) -> Result<WorkspaceInfo, String> {
    let stamp_path = PathBuf::from(file_path);
    unpack_stamp(&app, &stamp_path)
}

#[tauri::command]
fn preview_generate(workspace_id: String) -> Result<String, String> {
    let workspace_dir = get_workspace_dir(&workspace_id)?;
    let preview_path = workspace_dir.join("preview.png");

    // Attempt to find project root by looking for pyproject.toml
    let mut root_dir = std::env::current_dir().map_err(|e| e.to_string())?;
    loop {
        if root_dir.join("pyproject.toml").exists() {
            break;
        }
        if !root_dir.pop() {
            return Err("Could not find project root with pyproject.toml".to_string());
        }
    }

    let output = Command::new("uv")
        .current_dir(&root_dir)
        .args(&[
            "run",
            "serial-stamp",
            "preview",
            workspace_dir.to_str().ok_or("Invalid workspace path")?,
            "-o",
            preview_path.to_str().ok_or("Invalid preview path")?,
        ])
        .output()
        .map_err(|e| format!("Failed to execute python preview: {e}"))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        return Err(format!(
            "Preview generation failed.\nStdout: {stdout}\nStderr: {stderr}"
        ));
    }

    if !preview_path.exists() {
        return Err("Preview file was not created".to_string());
    }

    let image_data =
        fs::read(&preview_path).map_err(|e| format!("Failed to read preview file: {e}"))?;

    let b64 = base64::engine::general_purpose::STANDARD.encode(&image_data);
    Ok(b64)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Native menu items (Desktop). These are the main actions you requested to live in the native window menu.
    //
    // The behaviors (New/Open/Save/Save As/Export PDF) will be handled by the frontend.
    // We emit an app-level event whenever a menu item is selected.
    tauri::Builder::default()
        .setup(|app| {
            // Build menu
            let file_menu = Submenu::with_items(
                app,
                "File",
                true,
                &[
                    &MenuItem::with_id(app, "project.new", "New Project", true, None::<&str>)?,
                    &MenuItem::with_id(app, "project.open", "Open Project…", true, None::<&str>)?,
                    &MenuItem::with_id(app, "project.save", "Save Project", true, None::<&str>)?,
                    &MenuItem::with_id(
                        app,
                        "project.save_as",
                        "Save Project As…",
                        true,
                        None::<&str>,
                    )?,
                    &PredefinedMenuItem::separator(app)?,
                    &MenuItem::with_id(app, "export.pdf", "Export PDF…", true, None::<&str>)?,
                    &PredefinedMenuItem::separator(app)?,
                    &PredefinedMenuItem::quit(app, None::<&str>)?,
                ],
            )?;

            let menu = Menu::with_items(app, &[&file_menu])?;
            app.set_menu(menu)?;

            app.handle().plugin(tauri_plugin_dialog::init())?;

            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .on_menu_event(|app, event| {
            emit_menu_action(app, event.id().as_ref());
        })
        .invoke_handler(tauri::generate_handler![
            workspace_new,
            workspace_get_spec_json,
            workspace_set_spec_json,
            workspace_add_file,
            workspace_list_files,
            workspace_remove_file,
            project_pack,
            project_unpack,
            preview_generate
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
