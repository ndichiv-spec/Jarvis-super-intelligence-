use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum IntegrationType {
    Git,
    GitHub,
    Slack,
    Jira,
    Notion,
    Obsidian,
    VsCode,
    Docker,
    Postman,
    Terminal,
    Browser,
    Calendar,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrationContract {
    pub id: String,
    pub name: String,
    pub integration_type: IntegrationType,
    pub version: String,
    pub description: String,
    pub available: bool,
    pub docs_url: Option<String>,
}

pub struct IntegrationRegistry {
    contracts: Mutex<Vec<IntegrationContract>>,
}

impl IntegrationRegistry {
    pub fn new() -> Self {
        let contracts = vec![
            IntegrationContract {
                id: "int-git".into(),
                name: "Git".into(),
                integration_type: IntegrationType::Git,
                version: "1.0.0".into(),
                description: "Local Git repository operations".into(),
                available: true,
                docs_url: Some("https://git-scm.com/docs".into()),
            },
            IntegrationContract {
                id: "int-github".into(),
                name: "GitHub".into(),
                integration_type: IntegrationType::GitHub,
                version: "2.1.0".into(),
                description: "GitHub API integration for repositories and issues".into(),
                available: true,
                docs_url: Some("https://docs.github.com/en/rest".into()),
            },
            IntegrationContract {
                id: "int-slack".into(),
                name: "Slack".into(),
                integration_type: IntegrationType::Slack,
                version: "1.3.0".into(),
                description: "Slack messaging and notifications".into(),
                available: false,
                docs_url: Some("https://api.slack.com/docs".into()),
            },
            IntegrationContract {
                id: "int-vscode".into(),
                name: "VS Code".into(),
                integration_type: IntegrationType::VsCode,
                version: "1.0.0".into(),
                description: "Visual Studio Code editor integration".into(),
                available: true,
                docs_url: None,
            },
            IntegrationContract {
                id: "int-terminal".into(),
                name: "Terminal".into(),
                integration_type: IntegrationType::Terminal,
                version: "1.0.0".into(),
                description: "Native terminal emulator integration".into(),
                available: true,
                docs_url: None,
            },
            IntegrationContract {
                id: "int-docker".into(),
                name: "Docker".into(),
                integration_type: IntegrationType::Docker,
                version: "1.1.0".into(),
                description: "Docker container management".into(),
                available: false,
                docs_url: Some("https://docs.docker.com/reference".into()),
            },
            IntegrationContract {
                id: "int-browser".into(),
                name: "Browser".into(),
                integration_type: IntegrationType::Browser,
                version: "1.0.0".into(),
                description: "Web browser automation and tab management".into(),
                available: true,
                docs_url: None,
            },
        ];

        Self {
            contracts: Mutex::new(contracts),
        }
    }

    pub fn list_contracts(&self) -> Vec<IntegrationContract> {
        self.contracts.lock().unwrap().clone()
    }

    pub fn get_contract(&self, id: &str) -> Option<IntegrationContract> {
        self.contracts
            .lock()
            .unwrap()
            .iter()
            .find(|c| c.id == id)
            .cloned()
    }

    pub fn check_availability(&self, id: &str) -> Option<bool> {
        self.contracts
            .lock()
            .unwrap()
            .iter()
            .find(|c| c.id == id)
            .map(|c| c.available)
    }
}

impl Default for IntegrationRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[tauri::command]
pub fn get_integration_contracts(
    state: tauri::State<'_, IntegrationRegistry>,
) -> Vec<IntegrationContract> {
    state.list_contracts()
}
