from jarvis_core.domain.identity import (
    IdentityService,
    Permission,
    Profile,
    Role,
    User,
)
from jarvis_core.domain.shared.value_objects import DomainIdentifier, Email


def test_identity_service_permission_check() -> None:
    service = IdentityService()
    user = User(
        id=DomainIdentifier.new(),
        email=Email("user@example.com"),
        profile=Profile(display_name="User", timezone="UTC"),
        roles=(Role(name="admin", permissions=(Permission(key="manage:all"),)),),
        preferences=(),
        devices=(),
    )

    assert service.can(user, "manage:all") is True
    assert service.can(user, "read:only") is False
