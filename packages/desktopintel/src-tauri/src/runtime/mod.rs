use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeStatus {
    pub version: String,
    pub started_at: String,
    pub session_id: String,
    pub uptime_seconds: u64,
    pub capabilities: Vec<String>,
    pub gateway_connected: bool,
}

pub struct RuntimeState {
    pub version: String,
    pub started_at: DateTime<Utc>,
    pub session_id: Uuid,
    pub capabilities: Mutex<Vec<String>>,
    pub gateway_connected: Mutex<bool>,
}

impl RuntimeState {
    pub fn new() -> Self {
        Self {
            version: env!("CARGO_PKG_VERSION").to_string(),
            started_at: Utc::now(),
            session_id: Uuid::new_v4(),
            capabilities: Mutex::new(Vec::new()),
            gateway_connected: Mutex::new(false),
        }
    }

    pub fn start(&self) {
        let mut caps = self.capabilities.lock().unwrap();
        *caps = self.discover_capabilities();
    }

    pub fn shutdown(&self) {
        let mut gw = self.gateway_connected.lock().unwrap();
        *gw = false;
    }

    pub fn get_status(&self) -> RuntimeStatus {
        let elapsed = Utc::now() - self.started_at;
        let caps = self.capabilities.lock().unwrap().clone();
        let gw = *self.gateway_connected.lock().unwrap();

        RuntimeStatus {
            version: self.version.clone(),
            started_at: self.started_at.to_rfc3339(),
            session_id: self.session_id.to_string(),
            uptime_seconds: elapsed.num_seconds() as u64,
            capabilities: caps,
            gateway_connected: gw,
        }
    }

    pub fn discover_capabilities(&self) -> Vec<String> {
        vec![
            "file_interaction".into(),
            "notifications".into(),
            "sync".into(),
            "offline".into(),
            "updates".into(),
            "command_palette".into(),
            "diagnostics".into(),
            "audit".into(),
            "permissions".into(),
        ]
    }
}

impl Default for RuntimeState {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_runtime_status(state: tauri::State<'_, RuntimeState>) -> RuntimeStatus {
    state.get_status()
}
