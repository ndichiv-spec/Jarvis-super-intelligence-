use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PermissionType {
    FileSystemRead,
    FileSystemWrite,
    ClipboardRead,
    ClipboardWrite,
    NetworkAccess,
    NotificationSend,
    MicrophoneAccess,
    CameraAccess,
    LocationAccess,
    GatewayConnect,
    SyncAccess,
    SettingsRead,
    SettingsWrite,
    ExecuteCommand,
    AuditView,
}

impl PermissionType {
    pub fn all() -> Vec<Self> {
        vec![
            Self::FileSystemRead,
            Self::FileSystemWrite,
            Self::ClipboardRead,
            Self::ClipboardWrite,
            Self::NetworkAccess,
            Self::NotificationSend,
            Self::MicrophoneAccess,
            Self::CameraAccess,
            Self::LocationAccess,
            Self::GatewayConnect,
            Self::SyncAccess,
            Self::SettingsRead,
            Self::SettingsWrite,
            Self::ExecuteCommand,
            Self::AuditView,
        ]
    }

    pub fn description(&self) -> &str {
        match self {
            Self::FileSystemRead => "Read files on the local file system",
            Self::FileSystemWrite => "Write files to the local file system",
            Self::ClipboardRead => "Read from the system clipboard",
            Self::ClipboardWrite => "Write to the system clipboard",
            Self::NetworkAccess => "Make network requests",
            Self::NotificationSend => "Send desktop notifications",
            Self::MicrophoneAccess => "Access the microphone",
            Self::CameraAccess => "Access the camera",
            Self::LocationAccess => "Access location data",
            Self::GatewayConnect => "Connect to the JARVIS AI Gateway",
            Self::SyncAccess => "Access workspace sync functionality",
            Self::SettingsRead => "Read application settings",
            Self::SettingsWrite => "Modify application settings",
            Self::ExecuteCommand => "Execute privileged commands",
            Self::AuditView => "View audit logs",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PermissionGrant {
    pub id: String,
    pub permission_type: PermissionType,
    pub granted_at: String,
    pub expires_at: Option<String>,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PermissionRequest {
    pub id: String,
    pub permission_type: PermissionType,
    pub requested_at: String,
    pub reason: String,
    pub status: RequestStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RequestStatus {
    Pending,
    Granted,
    Denied,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PermissionEvent {
    pub id: String,
    pub permission_type: PermissionType,
    pub action: String,
    pub timestamp: String,
    pub success: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PermissionState {
    pub granted: Vec<PermissionGrant>,
    pub pending: Vec<PermissionRequest>,
    pub history: Vec<PermissionEvent>,
}

pub struct PermissionCenter {
    grants: Mutex<Vec<PermissionGrant>>,
    requests: Mutex<Vec<PermissionRequest>>,
    history: Mutex<Vec<PermissionEvent>>,
}

impl PermissionCenter {
    pub fn new() -> Self {
        Self {
            grants: Mutex::new(Vec::new()),
            requests: Mutex::new(Vec::new()),
            history: Mutex::new(Vec::new()),
        }
    }

    pub fn request(&self, permission: PermissionType, reason: &str) -> PermissionRequest {
        let req = PermissionRequest {
            id: uuid::Uuid::new_v4().to_string(),
            permission_type: permission,
            requested_at: Utc::now().to_rfc3339(),
            reason: reason.to_string(),
            status: RequestStatus::Pending,
        };
        self.requests.lock().unwrap().push(req.clone());
        self.history.lock().unwrap().push(PermissionEvent {
            id: uuid::Uuid::new_v4().to_string(),
            permission_type: permission,
            action: "requested".into(),
            timestamp: Utc::now().to_rfc3339(),
            success: true,
        });
        req
    }

    pub fn grant(&self, request_id: &str) -> Option<PermissionGrant> {
        let mut requests = self.requests.lock().unwrap();
        if let Some(req) = requests.iter_mut().find(|r| r.id == request_id) {
            req.status = RequestStatus::Granted;
            let grant = PermissionGrant {
                id: uuid::Uuid::new_v4().to_string(),
                permission_type: req.permission_type.clone(),
                granted_at: Utc::now().to_rfc3339(),
                expires_at: None,
                reason: req.reason.clone(),
            };
            self.grants.lock().unwrap().push(grant.clone());
            self.history.lock().unwrap().push(PermissionEvent {
                id: uuid::Uuid::new_v4().to_string(),
                permission_type: req.permission_type.clone(),
                action: "granted".into(),
                timestamp: Utc::now().to_rfc3339(),
                success: true,
            });
            Some(grant)
        } else {
            None
        }
    }

    pub fn deny(&self, request_id: &str) -> bool {
        let mut requests = self.requests.lock().unwrap();
        if let Some(req) = requests.iter_mut().find(|r| r.id == request_id) {
            req.status = RequestStatus::Denied;
            self.history.lock().unwrap().push(PermissionEvent {
                id: uuid::Uuid::new_v4().to_string(),
                permission_type: req.permission_type.clone(),
                action: "denied".into(),
                timestamp: Utc::now().to_rfc3339(),
                success: false,
            });
            true
        } else {
            false
        }
    }

    pub fn revoke(&self, grant_id: &str) -> bool {
        let mut grants = self.grants.lock().unwrap();
        if let Some(idx) = grants.iter().position(|g| g.id == grant_id) {
            let grant = grants.remove(idx);
            self.history.lock().unwrap().push(PermissionEvent {
                id: uuid::Uuid::new_v4().to_string(),
                permission_type: grant.permission_type,
                action: "revoked".into(),
                timestamp: Utc::now().to_rfc3339(),
                success: true,
            });
            true
        } else {
            false
        }
    }

    pub fn list_granted(&self) -> Vec<PermissionGrant> {
        self.grants.lock().unwrap().clone()
    }

    pub fn list_pending(&self) -> Vec<PermissionRequest> {
        self.requests
            .lock()
            .unwrap()
            .iter()
            .filter(|r| r.status == RequestStatus::Pending)
            .cloned()
            .collect()
    }

    pub fn list_history(&self) -> Vec<PermissionEvent> {
        self.history.lock().unwrap().clone()
    }

    pub fn get_state(&self) -> PermissionState {
        PermissionState {
            granted: self.list_granted(),
            pending: self.list_pending(),
            history: self.list_history(),
        }
    }
}

impl Default for PermissionCenter {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_permissions(state: tauri::State<'_, PermissionCenter>) -> PermissionState {
    state.get_state()
}

#[tauri::command]
pub fn request_permission(
    state: tauri::State<'_, PermissionCenter>,
    permission: PermissionType,
    reason: String,
) -> PermissionRequest {
    state.request(permission, &reason)
}

#[tauri::command]
pub fn grant_permission(
    state: tauri::State<'_, PermissionCenter>,
    request_id: String,
) -> Result<PermissionGrant, String> {
    state.grant(&request_id).ok_or_else(|| "Request not found".to_string())
}

#[tauri::command]
pub fn deny_permission(
    state: tauri::State<'_, PermissionCenter>,
    request_id: String,
) -> Result<bool, String> {
    if state.deny(&request_id) {
        Ok(true)
    } else {
        Err("Request not found".to_string())
    }
}

#[tauri::command]
pub fn revoke_permission(
    state: tauri::State<'_, PermissionCenter>,
    grant_id: String,
) -> Result<bool, String> {
    if state.revoke(&grant_id) {
        Ok(true)
    } else {
        Err("Grant not found".to_string())
    }
}
