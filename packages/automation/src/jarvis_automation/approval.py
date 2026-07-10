from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_automation.models import ApprovalRequest


@dataclass(slots=True)
class InMemoryApprovalEngine:
    _requests: dict[str, ApprovalRequest] = field(default_factory=dict)

    def request_approval(self, request: ApprovalRequest) -> ApprovalRequest:
        self._requests[request.approval_id] = request
        return request

    def approve(self, approval_id: str, approver: str) -> ApprovalRequest:
        req = self._requests.get(approval_id)
        if req is None:
            msg = f"Approval request not found: {approval_id}"
            raise KeyError(msg)
        updated = req.with_approval(approver)
        self._requests[approval_id] = updated
        return updated

    def reject(self, approval_id: str, approver: str) -> ApprovalRequest:
        req = self._requests.get(approval_id)
        if req is None:
            msg = f"Approval request not found: {approval_id}"
            raise KeyError(msg)
        updated = req.with_rejection(approver)
        self._requests[approval_id] = updated
        return updated

    def get_request(self, approval_id: str) -> ApprovalRequest | None:
        return self._requests.get(approval_id)

    def list_pending(self, execution_id: str) -> tuple[ApprovalRequest, ...]:
        return tuple(
            r for r in self._requests.values()
            if r.execution_id == execution_id and r.status.value == "pending"
        )

    def is_approved(self, approval_id: str) -> bool:
        req = self._requests.get(approval_id)
        if req is None:
            return False
        return req.status.value == "approved"
