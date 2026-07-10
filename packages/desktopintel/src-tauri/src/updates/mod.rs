use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ReleaseChannel {
    Stable,
    Beta,
    Nightly,
}

impl ReleaseChannel {
    pub fn as_str(&self) -> &str {
        match self {
            Self::Stable => "stable",
            Self::Beta => "beta",
            Self::Nightly => "nightly",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateStatus {
    pub current_version: String,
    pub update_available: bool,
    pub latest_version: Option<String>,
    pub release_channel: ReleaseChannel,
    pub last_check: Option<String>,
    pub download_progress: Option<f64>,
}

pub struct UpdateManager {
    current_version: String,
    channel: Mutex<ReleaseChannel>,
    update_available: Mutex<bool>,
    latest_version: Mutex<Option<String>>,
    last_check: Mutex<Option<DateTime<Utc>>>,
    download_progress: Mutex<Option<f64>>,
}

impl UpdateManager {
    pub fn new() -> Self {
        Self {
            current_version: env!("CARGO_PKG_VERSION").to_string(),
            channel: Mutex::new(ReleaseChannel::Stable),
            update_available: Mutex::new(false),
            latest_version: Mutex::new(None),
            last_check: Mutex::new(None),
            download_progress: Mutex::new(None),
        }
    }

    pub fn check_for_updates(&self) -> UpdateStatus {
        *self.last_check.lock().unwrap() = Some(Utc::now());
        *self.update_available.lock().unwrap() = false;
        *self.latest_version.lock().unwrap() = None;
        self.get_status()
    }

    pub async fn check_for_updates_async(&self) -> UpdateStatus {
        tokio::time::sleep(std::time::Duration::from_millis(300)).await;
        self.check_for_updates()
    }

    pub fn get_status(&self) -> UpdateStatus {
        UpdateStatus {
            current_version: self.current_version.clone(),
            update_available: *self.update_available.lock().unwrap(),
            latest_version: self.latest_version.lock().unwrap().clone(),
            release_channel: self.channel.lock().unwrap().clone(),
            last_check: self.last_check.lock().unwrap().map(|d| d.to_rfc3339()),
            download_progress: *self.download_progress.lock().unwrap(),
        }
    }

    pub fn apply_update(&self) -> Result<(), String> {
        let available = *self.update_available.lock().unwrap();
        if !available {
            return Err("No update available to apply".to_string());
        }
        *self.download_progress.lock().unwrap() = Some(100.0);
        Ok(())
    }

    pub fn rollback(&self) -> Result<(), String> {
        *self.update_available.lock().unwrap() = false;
        *self.latest_version.lock().unwrap() = None;
        *self.download_progress.lock().unwrap() = None;
        Ok(())
    }
}

impl Default for UpdateManager {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_update_status(state: tauri::State<'_, UpdateManager>) -> UpdateStatus {
    state.get_status()
}

#[tauri::command]
pub async fn check_updates(
    state: tauri::State<'_, UpdateManager>,
) -> UpdateStatus {
    state.check_for_updates_async().await
}
