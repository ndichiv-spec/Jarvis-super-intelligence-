from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class GatewayErrorCode(StrEnum):
    VALIDATION = "validation_error"
    AUTHORIZATION = "authorization_error"
    EXECUTION = "execution_error"
    INFRASTRUCTURE = "infrastructure_error"
    POLICY_VIOLATION = "policy_violation"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown_failure"


@dataclass(frozen=True, slots=True)
class GatewayErrorContract:
    code: GatewayErrorCode
    message: str
    status_code: int
    retryable: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "message": self.message,
            "status_code": self.status_code,
            "retryable": self.retryable,
            "details": dict(self.details),
        }


class GatewayException(Exception):  # noqa: N818
    def __init__(self, contract: GatewayErrorContract) -> None:
        self.contract = contract
        super().__init__(contract.message)

    @classmethod
    def validation(cls, message: str, *, details: dict[str, Any] | None = None) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.VALIDATION,
                message=message,
                status_code=400,
                details=details or {},
            )
        )

    @classmethod
    def authorization(
        cls,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.AUTHORIZATION,
                message=message,
                status_code=403,
                details=details or {},
            )
        )

    @classmethod
    def execution(cls, message: str, *, details: dict[str, Any] | None = None) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.EXECUTION,
                message=message,
                status_code=502,
                retryable=True,
                details=details or {},
            )
        )

    @classmethod
    def infrastructure(
        cls,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.INFRASTRUCTURE,
                message=message,
                status_code=503,
                retryable=True,
                details=details or {},
            )
        )

    @classmethod
    def policy_violation(
        cls,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.POLICY_VIOLATION,
                message=message,
                status_code=409,
                details=details or {},
            )
        )

    @classmethod
    def rate_limit(
        cls,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.RATE_LIMIT,
                message=message,
                status_code=429,
                retryable=True,
                details=details or {},
            )
        )

    @classmethod
    def unknown(
        cls,
        message: str = "An unknown gateway failure occurred",
        *,
        details: dict[str, Any] | None = None,
    ) -> GatewayException:
        return cls(
            GatewayErrorContract(
                code=GatewayErrorCode.UNKNOWN,
                message=message,
                status_code=500,
                retryable=False,
                details=details or {},
            )
        )
