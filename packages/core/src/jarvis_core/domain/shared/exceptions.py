class DomainError(Exception):
    """Base domain exception."""


class ValidationError(DomainError):
    """Raised when a domain invariant is violated."""
