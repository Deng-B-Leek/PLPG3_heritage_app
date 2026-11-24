
from enum import Enum


class Role(Enum):
    HEAD_OF_CULTURE = "Head of Culture"
    CULTURE_CHIEF = "Culture Chief"
    LOCAL_MEMBER = "Local Member"


class Permission(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


_ALL_PERMISSIONS = frozenset(Permission)

ROLE_PERMISSIONS = {
    Role.HEAD_OF_CULTURE: _ALL_PERMISSIONS,
    Role.CULTURE_CHIEF: frozenset({Permission.CREATE, Permission.READ, Permission.UPDATE}),
    Role.LOCAL_MEMBER: frozenset({Permission.CREATE, Permission.READ}),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]
