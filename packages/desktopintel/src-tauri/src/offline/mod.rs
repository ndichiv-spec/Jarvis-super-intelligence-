use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OfflineStatus {
    pub enabled: bool,
    pub cached_conversations: u64,
    pub cached_knowledge: u64,
    pub queued_actions: u64,
    pub last_sync: Option<String>,
    pub storage_used_bytes: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedConversation {
    pub id: String,
    pub title: String,
    pub cached_at: String,
    pub message_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedKnowledge {
    pub id: String,
    pub title: String,
    pub source: String,
    pub cached_at: String,
    pub size_bytes: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueuedAction {
    pub id: String,
    pub action_type: String,
    pub payload: String,
    pub queued_at: String,
    pub status: QueuedActionStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum QueuedActionStatus {
    Pending,
    InFlight,
    Completed,
    Failed(String),
}

pub struct OfflineManager {
    enabled: Mutex<bool>,
    conversations: Mutex<Vec<CachedConversation>>,
    knowledge: Mutex<Vec<CachedKnowledge>>,
    actions: Mutex<Vec<QueuedAction>>,
    last_sync: Mutex<Option<DateTime<Utc>>>,
}

impl OfflineManager {
    pub fn new() -> Self {
        Self {
            enabled: Mutex::new(false),
            conversations: Mutex::new(Vec::new()),
            knowledge: Mutex::new(Vec::new()),
            actions: Mutex::new(Vec::new()),
            last_sync: Mutex::new(None),
        }
    }

    pub fn toggle(&self) -> bool {
        let mut enabled = self.enabled.lock().unwrap();
        *enabled = !*enabled;
        *enabled
    }

    pub fn get_status(&self) -> OfflineStatus {
        let conv_count = self.conversations.lock().unwrap().len() as u64;
        let know_count = self.knowledge.lock().unwrap().len() as u64;
        let act_count = self.actions.lock().unwrap().len() as u64;
        let storage = (conv_count + know_count) * 1024;
        OfflineStatus {
            enabled: *self.enabled.lock().unwrap(),
            cached_conversations: conv_count,
            cached_knowledge: know_count,
            queued_actions: act_count,
            last_sync: self.last_sync.lock().unwrap().map(|d| d.to_rfc3339()),
            storage_used_bytes: storage,
        }
    }

    pub fn cache_conversation(&self, title: &str, message_count: u64) -> CachedConversation {
        let conv = CachedConversation {
            id: uuid::Uuid::new_v4().to_string(),
            title: title.to_string(),
            cached_at: Utc::now().to_rfc3339(),
            message_count,
        };
        self.conversations.lock().unwrap().push(conv.clone());
        conv
    }

    pub fn cache_knowledge(&self, title: &str, source: &str, size_bytes: u64) -> CachedKnowledge {
        let item = CachedKnowledge {
            id: uuid::Uuid::new_v4().to_string(),
            title: title.to_string(),
            source: source.to_string(),
            cached_at: Utc::now().to_rfc3339(),
            size_bytes,
        };
        self.knowledge.lock().unwrap().push(item.clone());
        item
    }

    pub fn queue_action(&self, action_type: &str, payload: &str) -> QueuedAction {
        let action = QueuedAction {
            id: uuid::Uuid::new_v4().to_string(),
            action_type: action_type.to_string(),
            payload: payload.to_string(),
            queued_at: Utc::now().to_rfc3339(),
            status: QueuedActionStatus::Pending,
        };
        self.actions.lock().unwrap().push(action.clone());
        action
    }

    pub fn resume_sync(&self) {
        *self.last_sync.lock().unwrap() = Some(Utc::now());
        let mut actions = self.actions.lock().unwrap();
        for action in actions.iter_mut() {
            match &action.status {
                QueuedActionStatus::Pending => {
                    action.status = QueuedActionStatus::Completed;
                }
                QueuedActionStatus::InFlight => {
                    action.status = QueuedActionStatus::Failed("connection lost".into());
                }
                _ => {}
            }
        }
    }

    pub fn list_conversations(&self) -> Vec<CachedConversation> {
        self.conversations.lock().unwrap().clone()
    }

    pub fn list_knowledge(&self) -> Vec<CachedKnowledge> {
        self.knowledge.lock().unwrap().clone()
    }

    pub fn list_actions(&self) -> Vec<QueuedAction> {
        self.actions.lock().unwrap().clone()
    }
}

impl Default for OfflineManager {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_offline_status(state: tauri::State<'_, OfflineManager>) -> OfflineStatus {
    state.get_status()
}

#[tauri::command]
pub fn toggle_offline(state: tauri::State<'_, OfflineManager>) -> bool {
    let enabled = state.toggle();
    if !enabled {
        state.resume_sync();
    }
    enabled
}

#[tauri::command]
pub fn get_cached_conversations(
    state: tauri::State<'_, OfflineManager>,
) -> Vec<CachedConversation> {
    state.list_conversations()
}

#[tauri::command]
pub fn get_cached_knowledge(
    state: tauri::State<'_, OfflineManager>,
) -> Vec<CachedKnowledge> {
    state.list_knowledge()
}

#[tauri::command]
pub fn get_queued_actions(state: tauri::State<'_, OfflineManager>) -> Vec<QueuedAction> {
    state.list_actions()
}
