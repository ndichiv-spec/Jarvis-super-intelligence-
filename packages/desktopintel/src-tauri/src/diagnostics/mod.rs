use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum HealthStatus {
    Healthy,
    Degraded,
    Unhealthy,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeHealth {
    pub status: HealthStatus,
    pub version: String,
    pub uptime_seconds: u64,
    pub session_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatewayHealth {
    pub status: HealthStatus,
    pub connected: bool,
    pub latency_ms: Option<u64>,
    pub last_ping: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncHealth {
    pub status: HealthStatus,
    pub last_sync: Option<String>,
    pub pending_items: u64,
    pub error_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceUsage {
    pub cpu_usage_percent: f32,
    pub memory_used_mb: u64,
    pub memory_total_mb: u64,
    pub disk_used_gb: u64,
    pub disk_total_gb: u64,
    pub process_memory_mb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiagnosticsReport {
    pub collected_at: String,
    pub runtime: RuntimeHealth,
    pub gateway: GatewayHealth,
    pub sync: SyncHealth,
    pub resources: ResourceUsage,
    pub permissions_count: u64,
    pub active_integrations: u64,
    pub notification_count: u64,
}

pub struct DiagnosticsCollector {
    last_report: Mutex<Option<DiagnosticsReport>>,
}

impl DiagnosticsCollector {
    pub fn new() -> Self {
        Self {
            last_report: Mutex::new(None),
        }
    }

    pub fn collect_all(
        &self,
        runtime_state: &crate::runtime::RuntimeState,
        sync_manager: &crate::sync::SyncManager,
        permission_center: &crate::permissions::PermissionCenter,
        integration_registry: &crate::integrations::IntegrationRegistry,
        notification_center: &crate::notifications::NotificationCenter,
    ) -> DiagnosticsReport {
        let runtime = self.check_runtime(runtime_state);
        let gateway = self.check_gateway(runtime_state);
        let sync = self.check_sync(sync_manager);
        let resources = self.check_resources();

        let report = DiagnosticsReport {
            collected_at: Utc::now().to_rfc3339(),
            runtime,
            gateway,
            sync,
            resources,
            permissions_count: permission_center.list_granted().len() as u64,
            active_integrations: integration_registry
                .list_contracts()
                .iter()
                .filter(|c| c.available)
                .count() as u64,
            notification_count: notification_center.list().len() as u64,
        };

        *self.last_report.lock().unwrap() = Some(report.clone());
        report
    }

    pub fn check_runtime(&self, state: &crate::runtime::RuntimeState) -> RuntimeHealth {
        let status = state.get_status();
        RuntimeHealth {
            status: HealthStatus::Healthy,
            version: status.version,
            uptime_seconds: status.uptime_seconds,
            session_id: status.session_id,
        }
    }

    pub fn check_gateway(&self, state: &crate::runtime::RuntimeState) -> GatewayHealth {
        let status = state.get_status();
        GatewayHealth {
            status: if status.gateway_connected {
                HealthStatus::Healthy
            } else {
                HealthStatus::Degraded
            },
            connected: status.gateway_connected,
            latency_ms: if status.gateway_connected { Some(12) } else { None },
            last_ping: if status.gateway_connected {
                Some(Utc::now().to_rfc3339())
            } else {
                None
            },
        }
    }

    pub fn check_sync(&self, manager: &crate::sync::SyncManager) -> SyncHealth {
        let status = manager.get_status();
        let error_count = status
            .modules
            .iter()
            .filter(|m| matches!(m.state, crate::sync::SyncState::Error(_)))
            .count() as u64;
        let pending = status
            .modules
            .iter()
            .filter(|m| {
                matches!(
                    m.state,
                    crate::sync::SyncState::Pending | crate::sync::SyncState::Syncing
                )
            })
            .count() as u64;

        SyncHealth {
            status: if error_count > 0 {
                HealthStatus::Degraded
            } else if pending > 0 {
                HealthStatus::Degraded
            } else {
                HealthStatus::Healthy
            },
            last_sync: status.last_full_sync,
            pending_items: pending,
            error_count,
        }
    }

    pub fn check_resources(&self) -> ResourceUsage {
        ResourceUsage {
            cpu_usage_percent: 0.0,
            memory_used_mb: 0,
            memory_total_mb: 0,
            disk_used_gb: 0,
            disk_total_gb: 0,
            process_memory_mb: 0,
        }
    }
}

impl Default for DiagnosticsCollector {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub async fn get_diagnostics(
    state: tauri::State<'_, DiagnosticsCollector>,
    app: tauri::AppHandle,
) -> DiagnosticsReport {
    let runtime_state = app.state::<crate::runtime::RuntimeState>();
    let sync_manager = app.state::<crate::sync::SyncManager>();
    let permission_center = app.state::<crate::permissions::PermissionCenter>();
    let integration_registry = app.state::<crate::integrations::IntegrationRegistry>();
    let notification_center = app.state::<crate::notifications::NotificationCenter>();

    state.collect_all(
        &runtime_state.inner(),
        &sync_manager.inner(),
        &permission_center.inner(),
        &integration_registry.inner(),
        &notification_center.inner(),
    )
}
