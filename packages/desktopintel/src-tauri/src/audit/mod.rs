use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEvent {
    pub id: String,
    pub timestamp: String,
    pub module: String,
    pub action: String,
    pub description: String,
    pub success: bool,
}

pub struct AuditLogger {
    events: Mutex<Vec<AuditEvent>>,
}

impl AuditLogger {
    pub fn new() -> Self {
        Self {
            events: Mutex::new(Vec::new()),
        }
    }

    pub fn log_event(
        &self,
        module: &str,
        action: &str,
        description: &str,
        success: bool,
    ) -> AuditEvent {
        let event = AuditEvent {
            id: uuid::Uuid::new_v4().to_string(),
            timestamp: Utc::now().to_rfc3339(),
            module: module.to_string(),
            action: action.to_string(),
            description: description.to_string(),
            success,
        };
        let mut events = self.events.lock().unwrap();
        events.push(event.clone());
        event
    }

    pub fn list_events(&self) -> Vec<AuditEvent> {
        self.events.lock().unwrap().clone()
    }

    pub fn get_by_module(&self, module: &str) -> Vec<AuditEvent> {
        self.events
            .lock()
            .unwrap()
            .iter()
            .filter(|e| e.module == module)
            .cloned()
            .collect()
    }

    pub fn get_by_action(&self, action: &str) -> Vec<AuditEvent> {
        self.events
            .lock()
            .unwrap()
            .iter()
            .filter(|e| e.action == action)
            .cloned()
            .collect()
    }
}

impl Default for AuditLogger {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_audit_events(
    state: tauri::State<'_, AuditLogger>,
    module: Option<String>,
    action: Option<String>,
) -> Vec<AuditEvent> {
    match (module, action) {
        (Some(m), None) => state.get_by_module(&m),
        (None, Some(a)) => state.get_by_action(&a),
        (Some(m), Some(a)) => state
            .list_events()
            .into_iter()
            .filter(|e| e.module == m && e.action == a)
            .collect(),
        (None, None) => state.list_events(),
    }
}
