use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri_plugin_dialog::DialogExt;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FileOpType {
    Open,
    Save,
    Move,
    Copy,
    Delete,
    Rename,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileOperation {
    pub id: String,
    pub op_type: FileOpType,
    pub path: Option<String>,
    pub timestamp: String,
    pub success: bool,
}

pub struct FileInteraction {
    operations: Mutex<Vec<FileOperation>>,
}

impl FileInteraction {
    pub fn new() -> Self {
        Self {
            operations: Mutex::new(Vec::new()),
        }
    }

    pub fn record_operation(
        &self,
        op_type: FileOpType,
        path: Option<String>,
        success: bool,
    ) -> FileOperation {
        let op = FileOperation {
            id: uuid::Uuid::new_v4().to_string(),
            op_type,
            path,
            timestamp: Utc::now().to_rfc3339(),
            success,
        };
        self.operations.lock().unwrap().push(op.clone());
        op
    }

    pub fn get_operations(&self) -> Vec<FileOperation> {
        self.operations.lock().unwrap().clone()
    }
}

impl Default for FileInteraction {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_file_operations(state: tauri::State<'_, FileInteraction>) -> Vec<FileOperation> {
    state.get_operations()
}

#[tauri::command]
pub async fn open_file(app: tauri::AppHandle) -> Result<Option<String>, String> {
    let file = app
        .dialog()
        .file()
        .add_filter("All Files", &["*"])
        .blocking_pick_file();
    match file {
        Some(path) => Ok(Some(path.to_string())),
        None => Ok(None),
    }
}

#[tauri::command]
pub async fn save_file(app: tauri::AppHandle) -> Result<Option<String>, String> {
    let file = app
        .dialog()
        .file()
        .add_filter("All Files", &["*"])
        .blocking_save_file();
    match file {
        Some(path) => Ok(Some(path.to_string())),
        None => Ok(None),
    }
}
