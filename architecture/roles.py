
from enum import Enum


class Role(Enum):
    ORGANIZER = "Community Cultural Organizer"
    GROUP_LEADER = "Cultural Group Leader"
    VOLUNTEER = "Local Heritage Volunteer"


class Permission(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


_ALL_PERMISSIONS = frozenset(Permission)

ROLE_PERMISSIONS = {
    Role.ORGANIZER: _ALL_PERMISSIONS,
    Role.GROUP_LEADER: _ALL_PERMISSIONS,
    Role.VOLUNTEER: frozenset({Permission.CREATE, Permission.READ}),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]
