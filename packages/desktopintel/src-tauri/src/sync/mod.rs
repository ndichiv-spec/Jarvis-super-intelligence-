use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SyncState {
    Synced,
    Syncing,
    Pending,
    Error(String),
    Offline,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncModule {
    pub name: String,
    pub state: SyncState,
    pub last_sync: Option<String>,
    pub item_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncStatus {
    pub overall_state: SyncState,
    pub modules: Vec<SyncModule>,
    pub last_full_sync: Option<String>,
}

pub struct SyncManager {
    modules: Mutex<Vec<SyncModule>>,
    last_full_sync: Mutex<Option<DateTime<Utc>>>,
    overall_state: Mutex<SyncState>,
}

impl SyncManager {
    pub fn new() -> Self {
        let modules = vec![
            SyncModule {
                name: "conversations".into(),
                state: SyncState::Synced,
                last_sync: Some(Utc::now().to_rfc3339()),
                item_count: 0,
            },
            SyncModule {
                name: "knowledge".into(),
                state: SyncState::Synced,
                last_sync: Some(Utc::now().to_rfc3339()),
                item_count: 0,
            },
            SyncModule {
                name: "settings".into(),
                state: SyncState::Synced,
                last_sync: Some(Utc::now().to_rfc3339()),
                item_count: 5,
            },
        ];

        Self {
            modules: Mutex::new(modules),
            last_full_sync: Mutex::new(Some(Utc::now())),
            overall_state: Mutex::new(SyncState::Synced),
        }
    }

    pub fn start_sync(&self) {
        *self.overall_state.lock().unwrap() = SyncState::Syncing;
        let mut modules = self.modules.lock().unwrap();
        for module in modules.iter_mut() {
            module.state = SyncState::Syncing;
        }
    }

    pub fn get_status(&self) -> SyncStatus {
        let modules = self.modules.lock().unwrap().clone();
        let overall = self.overall_state.lock().unwrap().clone();
        let last = self.last_full_sync.lock().unwrap().map(|d| d.to_rfc3339());

        SyncStatus {
            overall_state: overall,
            modules,
            last_full_sync: last,
        }
    }

    pub fn get_modules(&self) -> Vec<SyncModule> {
        self.modules.lock().unwrap().clone()
    }

    pub fn resolve_conflicts(&self) -> u64 {
        let mut modules = self.modules.lock().unwrap();
        for module in modules.iter_mut() {
            if matches!(module.state, SyncState::Error(_)) {
                module.state = SyncState::Pending;
                module.last_sync = Some(Utc::now().to_rfc3339());
            }
        }
        modules.iter().filter(|m| m.state == SyncState::Pending).count() as u64
    }
}

impl Default for SyncManager {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_sync_status(state: tauri::State<'_, SyncManager>) -> SyncStatus {
    state.get_status()
}

#[tauri::command]
pub async fn trigger_sync(
    state: tauri::State<'_, SyncManager>,
) -> Result<SyncStatus, String> {
    state.start_sync();
    tokio::time::sleep(std::time::Duration::from_millis(500)).await;
    let mut modules = state.modules.lock().unwrap();
    for module in modules.iter_mut() {
        module.state = SyncState::Synced;
        module.last_sync = Some(Utc::now().to_rfc3339());
        module.item_count += 1;
    }
    drop(modules);
    *state.overall_state.lock().unwrap() = SyncState::Synced;
    *state.last_full_sync.lock().unwrap() = Some(Utc::now());
    Ok(state.get_status())
}
