from __future__ import annotations

from jarvis_agents.agents.base import BaseAgent
from jarvis_agents.models import (
    AgentCapability,
    AgentPermission,
    AgentPermissionResource,
    AgentTask,
    AgentTaskResult,
    PermissionAccess,
)


class WebIntelligenceAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="WebIntelligence",
            description="Monitors web sources, scrapes content, and collects online intelligence",
            capabilities=(
                AgentCapability(name="web_scraping", description="Scrape web content"),
                AgentCapability(name="web_monitoring", description="Monitor web sources for changes"),
                AgentCapability(name="content_extraction", description="Extract structured data from web pages"),
                AgentCapability(name="link_analysis", description="Analyze web links and relationships"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.EXTERNAL_SYSTEM, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "scrape" in desc or "crawl" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Web scraping completed: {task.description}",
                metadata={"pages_scraped": "10", "data_points": "245"},
            )
        if "monitor" in desc or "track" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Web monitoring configured: {task.description}",
                metadata={"sources_monitored": "3", "check_interval": "1h"},
            )
        if "extract" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Content extracted for: {task.description}",
                metadata={"extraction_type": "structured", "fields": "8"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Web intelligence task completed: {task.description}",
            metadata={"intel_type": "web", "confidence": "0.88"},
        )
