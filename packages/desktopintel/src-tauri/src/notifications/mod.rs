use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationItem {
    pub id: String,
    pub title: String,
    pub body: String,
    pub notification_type: String,
    pub timestamp: String,
    pub read: bool,
    pub action_url: Option<String>,
}

pub struct NotificationCenter {
    notifications: Mutex<Vec<NotificationItem>>,
}

impl NotificationCenter {
    pub fn new() -> Self {
        Self {
            notifications: Mutex::new(Vec::new()),
        }
    }

    pub fn send(
        &self,
        title: &str,
        body: &str,
        notification_type: &str,
        action_url: Option<String>,
    ) -> NotificationItem {
        let item = NotificationItem {
            id: uuid::Uuid::new_v4().to_string(),
            title: title.to_string(),
            body: body.to_string(),
            notification_type: notification_type.to_string(),
            timestamp: Utc::now().to_rfc3339(),
            read: false,
            action_url,
        };
        self.notifications.lock().unwrap().push(item.clone());
        item
    }

    pub fn list(&self) -> Vec<NotificationItem> {
        self.notifications.lock().unwrap().clone()
    }

    pub fn mark_read(&self, id: &str) -> bool {
        let mut notifications = self.notifications.lock().unwrap();
        if let Some(item) = notifications.iter_mut().find(|n| n.id == id) {
            item.read = true;
            true
        } else {
            false
        }
    }

    pub fn clear(&self) {
        self.notifications.lock().unwrap().clear();
    }

    pub fn send_native(
        &self,
        app: &tauri::AppHandle,
        title: &str,
        body: &str,
    ) -> Result<(), String> {
        use tauri_plugin_notification::NotificationExt;
        app.notification()
            .builder()
            .title(title)
            .body(body)
            .show()
            .map_err(|e| e.to_string())?;
        self.send(title, body, "native", None);
        Ok(())
    }
}

impl Default for NotificationCenter {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_notifications(state: tauri::State<'_, NotificationCenter>) -> Vec<NotificationItem> {
    state.list()
}

#[tauri::command]
pub fn mark_notification_read(
    state: tauri::State<'_, NotificationCenter>,
    id: String,
) -> Result<bool, String> {
    if state.mark_read(&id) {
        Ok(true)
    } else {
        Err("Notification not found".to_string())
    }
}

#[tauri::command]
pub fn clear_notifications(state: tauri::State<'_, NotificationCenter>) {
    state.clear();
}
