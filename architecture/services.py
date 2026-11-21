
import sqlite3

from .errors import PermissionDenied, RecordNotFound, StorageError
from .roles import Permission, has_permission
from .validators import (
    MAX_LONG_TEXT,
    clean_date,
    clean_record_id,
    clean_text,
)

TRADITIONS = "traditions"
EVENTS = "events"
_TABLES = {TRADITIONS, EVENTS}


class HeritageService:
    def __init__(self, db, role):
        self.db = db
        self.role = role

    def can(self, permission):
        return has_permission(self.role, permission)

    def _require(self, permission):
        if not self.can(permission):
            raise PermissionDenied(
                f"The role '{self.role.value}' is not allowed to {permission.value} records."
            )

    def _write(self, sql, params=()):
        try:
            return self.db.execute(sql, params)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save changes: {exc}") from exc

    def _read(self, sql, params=()):
        try:
            return self.db.fetch_all(sql, params)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not read records: {exc}") from exc

    def _check_table(self, table):
        if table not in _TABLES:
            raise ValueError(f"Unknown table: {table}")

    def add_tradition(self, name, community, description):
        self._require(Permission.CREATE)
        name = clean_text(name, "Tradition name")
        community = clean_text(community, "Community")
        description = clean_text(description, "Description", MAX_LONG_TEXT)
        cursor = self._write(
            "INSERT INTO traditions (name, community, description, created_by) "
            "VALUES (?, ?, ?, ?)",
            (name, community, description, self.role.value),
        )
        return cursor.lastrowid

    def add_event(self, event_name, event_date, location):
        self._require(Permission.CREATE)
        event_name = clean_text(event_name, "Event name")
        event_date = clean_date(event_date)
        location = clean_text(location, "Location")
        cursor = self._write(
            "INSERT INTO events (event_name, event_date, location, created_by) "
            "VALUES (?, ?, ?, ?)",
            (event_name, event_date, location, self.role.value),
        )
        return cursor.lastrowid

    def list_traditions(self, keyword=None):
        self._require(Permission.READ)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            rows = self._read(
                "SELECT * FROM traditions WHERE name LIKE ? OR community LIKE ? "
                "ORDER BY id",
                (pattern, pattern),
            )
        else:
            rows = self._read("SELECT * FROM traditions ORDER BY id")
        return [dict(row) for row in rows]

    def list_events(self, keyword=None):
        self._require(Permission.READ)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            rows = self._read(
                "SELECT * FROM events WHERE event_name LIKE ? OR location LIKE ? "
                "ORDER BY event_date, id",
                (pattern, pattern),
            )
        else:
            rows = self._read("SELECT * FROM events ORDER BY event_date, id")
        return [dict(row) for row in rows]

    def get_record(self, table, record_id):
        self._require(Permission.READ)
        self._check_table(table)
        record_id = clean_record_id(record_id)
        try:
            row = self.db.fetch_one(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        except sqlite3.Error as exc:
            raise StorageError(f"Could not read record: {exc}") from exc
        if row is None:
            raise RecordNotFound(f"No record with ID {record_id} was found.")
        return dict(row)

    def update_tradition(self, record_id, name, community, description):
        self._require(Permission.UPDATE)
        self.get_record(TRADITIONS, record_id)
        record_id = clean_record_id(record_id)
        self._write(
            "UPDATE traditions SET name = ?, community = ?, description = ? WHERE id = ?",
            (
                clean_text(name, "Tradition name"),
                clean_text(community, "Community"),
                clean_text(description, "Description", MAX_LONG_TEXT),
                record_id,
            ),
        )

    def update_event(self, record_id, event_name, event_date, location):
        self._require(Permission.UPDATE)
        self.get_record(EVENTS, record_id)
        record_id = clean_record_id(record_id)
        self._write(
            "UPDATE events SET event_name = ?, event_date = ?, location = ? WHERE id = ?",
            (
                clean_text(event_name, "Event name"),
                clean_date(event_date),
                clean_text(location, "Location"),
                record_id,
            ),
        )

    def delete_record(self, table, record_id):
        self._require(Permission.DELETE)
        self._check_table(table)
        self.get_record(table, record_id)
        record_id = clean_record_id(record_id)
        self._write(f"DELETE FROM {table} WHERE id = ?", (record_id,))
