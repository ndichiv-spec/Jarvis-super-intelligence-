from __future__ import annotations

from typing import Any


class TemplateEngine:
    def __init__(self) -> None:
        self._templates: dict[str, str] = {}

    def register(self, template_name: str, template: str) -> None:
        self._templates[template_name] = template

    def render(self, template_name: str, **kwargs: Any) -> str:
        template = self._templates.get(template_name)
        if template is None:
            raise ValueError(f"Template '{template_name}' not found")
        return template.format(**kwargs)

    def unregister(self, template_name: str) -> None:
        self._templates.pop(template_name, None)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def register_email_template(self, template_name: str, subject: str, body: str) -> None:
        self.register(f"email:{template_name}:subject", subject)
        self.register(f"email:{template_name}:body", body)

    def render_email(self, template_name: str, **kwargs: Any) -> dict[str, str]:
        subject = self.render(f"email:{template_name}:subject", **kwargs)
        body = self.render(f"email:{template_name}:body", **kwargs)
        return {"subject": subject, "body": body}

    def register_notification_template(self, template_name: str, title: str, body: str) -> None:
        self.register(f"notification:{template_name}:title", title)
        self.register(f"notification:{template_name}:body", body)

    def render_notification(self, template_name: str, **kwargs: Any) -> dict[str, str]:
        title = self.render(f"notification:{template_name}:title", **kwargs)
        body = self.render(f"notification:{template_name}:body", **kwargs)
        return {"title": title, "body": body}

    def register_report_template(self, template_name: str, template: str) -> None:
        self.register(f"report:{template_name}", template)

    def render_report(self, template_name: str, **kwargs: Any) -> str:
        return self.render(f"report:{template_name}", **kwargs)

    def register_system_template(self, template_name: str, template: str) -> None:
        self.register(f"system:{template_name}", template)

    def render_system_message(self, template_name: str, **kwargs: Any) -> str:
        return self.render(f"system:{template_name}", **kwargs)

    def register_agent_template(self, template_name: str, template: str) -> None:
        self.register(f"agent:{template_name}", template)

    def render_agent_message(self, template_name: str, **kwargs: Any) -> str:
        return self.render(f"agent:{template_name}", **kwargs)

    def register_meeting_summary_template(self, template_name: str, template: str) -> None:
        self.register(f"meeting:{template_name}:summary", template)

    def render_meeting_summary(self, template_name: str, **kwargs: Any) -> str:
        return self.render(f"meeting:{template_name}:summary", **kwargs)

    @property
    def total_templates(self) -> int:
        return len(self._templates)
