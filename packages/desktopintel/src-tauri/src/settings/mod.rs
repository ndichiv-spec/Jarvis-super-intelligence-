use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowSettings {
    pub width: u32,
    pub height: u32,
    pub x: Option<i32>,
    pub y: Option<i32>,
    pub maximized: bool,
    pub fullscreen: bool,
}

impl Default for WindowSettings {
    fn default() -> Self {
        Self {
            width: 1200,
            height: 800,
            x: None,
            y: None,
            maximized: false,
            fullscreen: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThemeSettings {
    pub mode: String,
    pub accent_color: String,
    pub font_size: u32,
    pub font_family: String,
}

impl Default for ThemeSettings {
    fn default() -> Self {
        Self {
            mode: "system".into(),
            accent_color: "#0078D4".into(),
            font_size: 14,
            font_family: "Segoe UI".into(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncSettings {
    pub auto_sync: bool,
    pub sync_interval_seconds: u64,
    pub conflict_resolution: String,
}

impl Default for SyncSettings {
    fn default() -> Self {
        Self {
            auto_sync: true,
            sync_interval_seconds: 300,
            conflict_resolution: "manual".into(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationSettings {
    pub enabled: bool,
    pub show_desktop_notifications: bool,
    pub sound_enabled: bool,
    pub do_not_disturb: bool,
}

impl Default for NotificationSettings {
    fn default() -> Self {
        Self {
            enabled: true,
            show_desktop_notifications: true,
            sound_enabled: true,
            do_not_disturb: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrivacySettings {
    pub collect_telemetry: bool,
    pub crash_reports: bool,
    pub local_processing_only: bool,
}

impl Default for PrivacySettings {
    fn default() -> Self {
        Self {
            collect_telemetry: false,
            crash_reports: true,
            local_processing_only: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OfflineSettings {
    pub max_cached_conversations: u32,
    pub max_cached_knowledge_items: u32,
    pub auto_cache_recent: bool,
}

impl Default for OfflineSettings {
    fn default() -> Self {
        Self {
            max_cached_conversations: 50,
            max_cached_knowledge_items: 200,
            auto_cache_recent: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateSettings {
    pub channel: String,
    pub auto_check: bool,
    pub auto_download: bool,
}

impl Default for UpdateSettings {
    fn default() -> Self {
        Self {
            channel: "stable".into(),
            auto_check: true,
            auto_download: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DesktopSettings {
    pub window: WindowSettings,
    pub theme: ThemeSettings,
    pub sync: SyncSettings,
    pub notifications: NotificationSettings,
    pub privacy: PrivacySettings,
    pub offline: OfflineSettings,
    pub updates: UpdateSettings,
}

impl Default for DesktopSettings {
    fn default() -> Self {
        Self {
            window: WindowSettings::default(),
            theme: ThemeSettings::default(),
            sync: SyncSettings::default(),
            notifications: NotificationSettings::default(),
            privacy: PrivacySettings::default(),
            offline: OfflineSettings::default(),
            updates: UpdateSettings::default(),
        }
    }
}

fn settings_path() -> PathBuf {
    let base = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
    base.join("jarvis-desktop-intelligence").join("settings.json")
}

pub struct SettingsManager {
    settings: Mutex<DesktopSettings>,
    path: PathBuf,
}

impl SettingsManager {
    pub fn new() -> Self {
        let path = settings_path();
        let settings = Self::load_from_disk(&path).unwrap_or_default();
        Self {
            settings: Mutex::new(settings),
            path,
        }
    }

    fn load_from_disk(path: &PathBuf) -> Option<DesktopSettings> {
        if !path.exists() {
            return None;
        }
        let content = std::fs::read_to_string(path).ok()?;
        serde_json::from_str(&content).ok()
    }

    fn save_to_disk(&self) -> Result<(), String> {
        if let Some(parent) = self.path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let settings = self.settings.lock().unwrap();
        let content = serde_json::to_string_pretty(&*settings).map_err(|e| e.to_string())?;
        std::fs::write(&self.path, content).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn load(&self) -> DesktopSettings {
        self.settings.lock().unwrap().clone()
    }

    pub fn save(&self) -> Result<(), String> {
        self.save_to_disk()
    }

    pub fn get(&self) -> DesktopSettings {
        self.load()
    }

    pub fn update(&self, new_settings: DesktopSettings) -> Result<DesktopSettings, String> {
        *self.settings.lock().unwrap() = new_settings.clone();
        self.save_to_disk()?;
        Ok(new_settings)
    }
}

impl Default for SettingsManager {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_settings(state: tauri::State<'_, SettingsManager>) -> DesktopSettings {
    state.get()
}

#[tauri::command]
pub fn apply_settings(
    state: tauri::State<'_, SettingsManager>,
    settings: DesktopSettings,
) -> Result<DesktopSettings, String> {
    state.update(settings)
}
