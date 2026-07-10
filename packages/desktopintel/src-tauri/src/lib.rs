mod runtime;
mod permissions;
mod sync;
mod file_interaction;
mod integrations;
mod notifications;
mod offline;
mod updates;
mod palette;
mod settings;
mod diagnostics;
mod audit;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(runtime::RuntimeState::new())
        .manage(permissions::PermissionCenter::new())
        .manage(sync::SyncManager::new())
        .manage(file_interaction::FileInteraction::new())
        .manage(integrations::IntegrationRegistry::new())
        .manage(notifications::NotificationCenter::new())
        .manage(offline::OfflineManager::new())
        .manage(updates::UpdateManager::new())
        .manage(palette::CommandRegistry::new())
        .manage(settings::SettingsManager::new())
        .manage(diagnostics::DiagnosticsCollector::new())
        .manage(audit::AuditLogger::new())
        .invoke_handler(tauri::generate_handler![
            runtime::get_runtime_status,
            permissions::get_permissions,
            permissions::request_permission,
            permissions::grant_permission,
            permissions::deny_permission,
            permissions::revoke_permission,
            sync::get_sync_status,
            sync::trigger_sync,
            file_interaction::get_file_operations,
            file_interaction::open_file,
            file_interaction::save_file,
            integrations::get_integration_contracts,
            notifications::get_notifications,
            notifications::mark_notification_read,
            notifications::clear_notifications,
            offline::get_offline_status,
            offline::toggle_offline,
            offline::get_cached_conversations,
            offline::get_cached_knowledge,
            offline::get_queued_actions,
            updates::get_update_status,
            updates::check_updates,
            palette::get_commands,
            settings::get_settings,
            settings::apply_settings,
            diagnostics::get_diagnostics,
            audit::get_audit_events,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
