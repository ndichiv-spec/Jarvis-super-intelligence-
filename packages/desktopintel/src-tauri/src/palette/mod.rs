use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CommandCategory {
    File,
    Edit,
    View,
    Navigate,
    Sync,
    Tools,
    Help,
    Developer,
    Settings,
    Integrations,
    Notifications,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DesktopCommand {
    pub id: String,
    pub name: String,
    pub description: String,
    pub category: CommandCategory,
    pub shortcut: Option<String>,
    pub icon: Option<String>,
}

pub struct CommandRegistry {
    commands: Mutex<Vec<DesktopCommand>>,
}

impl CommandRegistry {
    pub fn new() -> Self {
        let commands = vec![
            DesktopCommand {
                id: "cmd-open-file".into(),
                name: "Open File".into(),
                description: "Open a file from the local filesystem".into(),
                category: CommandCategory::File,
                shortcut: Some("Ctrl+O".into()),
                icon: Some("file-open".into()),
            },
            DesktopCommand {
                id: "cmd-save-file".into(),
                name: "Save File".into(),
                description: "Save the current file".into(),
                category: CommandCategory::File,
                shortcut: Some("Ctrl+S".into()),
                icon: Some("file-save".into()),
            },
            DesktopCommand {
                id: "cmd-sync".into(),
                name: "Trigger Sync".into(),
                description: "Start workspace synchronization".into(),
                category: CommandCategory::Sync,
                shortcut: Some("Ctrl+Shift+S".into()),
                icon: Some("sync".into()),
            },
            DesktopCommand {
                id: "cmd-toggle-offline".into(),
                name: "Toggle Offline Mode".into(),
                description: "Enable or disable offline mode".into(),
                category: CommandCategory::Settings,
                shortcut: Some("Ctrl+Shift+O".into()),
                icon: Some("offline".into()),
            },
            DesktopCommand {
                id: "cmd-check-updates".into(),
                name: "Check for Updates".into(),
                description: "Check for available application updates".into(),
                category: CommandCategory::Tools,
                shortcut: None,
                icon: Some("update".into()),
            },
            DesktopCommand {
                id: "cmd-notifications".into(),
                name: "Show Notifications".into(),
                description: "View all notifications".into(),
                category: CommandCategory::Notifications,
                shortcut: Some("Ctrl+N".into()),
                icon: Some("bell".into()),
            },
            DesktopCommand {
                id: "cmd-settings".into(),
                name: "Open Settings".into(),
                description: "Open the application settings".into(),
                category: CommandCategory::Settings,
                shortcut: Some("Ctrl+,".into()),
                icon: Some("gear".into()),
            },
            DesktopCommand {
                id: "cmd-diagnostics".into(),
                name: "Run Diagnostics".into(),
                description: "Collect and view system diagnostics".into(),
                category: CommandCategory::Developer,
                shortcut: Some("Ctrl+Shift+D".into()),
                icon: Some("diagnostics".into()),
            },
            DesktopCommand {
                id: "cmd-audit-log".into(),
                name: "View Audit Log".into(),
                description: "View the security audit log".into(),
                category: CommandCategory::Developer,
                shortcut: None,
                icon: Some("audit".into()),
            },
            DesktopCommand {
                id: "cmd-permissions".into(),
                name: "Manage Permissions".into(),
                description: "View and manage application permissions".into(),
                category: CommandCategory::Settings,
                shortcut: None,
                icon: Some("shield".into()),
            },
            DesktopCommand {
                id: "cmd-integrations".into(),
                name: "Browse Integrations".into(),
                description: "View available integration contracts".into(),
                category: CommandCategory::Integrations,
                shortcut: Some("Ctrl+Shift+I".into()),
                icon: Some("puzzle".into()),
            },
            DesktopCommand {
                id: "cmd-runtime-status".into(),
                name: "Runtime Status".into(),
                description: "View desktop runtime status information".into(),
                category: CommandCategory::Developer,
                shortcut: None,
                icon: Some("info".into()),
            },
        ];

        Self {
            commands: Mutex::new(commands),
        }
    }

    pub fn list_commands(&self) -> Vec<DesktopCommand> {
        self.commands.lock().unwrap().clone()
    }

    pub fn search(&self, query: &str) -> Vec<DesktopCommand> {
        let lower = query.to_lowercase();
        self.commands
            .lock()
            .unwrap()
            .iter()
            .filter(|c| {
                c.name.to_lowercase().contains(&lower)
                    || c.description.to_lowercase().contains(&lower)
                    || c.category.to_string().to_lowercase().contains(&lower)
            })
            .cloned()
            .collect()
    }

    pub fn execute(&self, command_id: &str) -> Option<DesktopCommand> {
        self.commands
            .lock()
            .unwrap()
            .iter()
            .find(|c| c.id == command_id)
            .cloned()
    }
}

impl Default for CommandRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_commands(
    state: tauri::State<'_, CommandRegistry>,
    query: Option<String>,
) -> Vec<DesktopCommand> {
    match query {
        Some(q) if !q.is_empty() => state.search(&q),
        _ => state.list_commands(),
    }
}
