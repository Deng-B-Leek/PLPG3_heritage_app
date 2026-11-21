class HeritageError(Exception):
    pass


class ValidationError(HeritageError):
    pass


class PermissionDenied(HeritageError):
    pass


class RecordNotFound(HeritageError):
    pass


class StorageError(HeritageError):
    pass
