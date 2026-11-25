import sqlite3

from .errors import HeritageError
from .roles import CREATE, DELETE, READ, UPDATE, has_permission
from .validators import MAX_LONG_TEXT, clean_date, clean_record_id, clean_text

TRADITIONS = "traditions"
EVENTS = "events"
TABLES = [TRADITIONS, EVENTS]

TRADITION_COLUMNS = ["id", "name", "community", "description", "created_by"]
EVENT_COLUMNS = ["id", "event_name", "event_date", "location", "created_by"]


def row_to_dict(columns, row):
    record = {}
    for i in range(len(columns)):
        record[columns[i]] = row[i]
    return record


class HeritageService:
    def __init__(self, db, role):
        self.db = db
        self.role = role

    def can(self, permission):
        return has_permission(self.role, permission)

    def _require(self, permission):
        if not self.can(permission):
            raise HeritageError(
                f"The role '{self.role}' is not allowed to {permission} records."
            )

    def _write(self, sql, params=()):
        try:
            self.db.execute(sql, params)
        except sqlite3.Error as exc:
            raise HeritageError(f"Could not save changes: {exc}")

    def _read(self, sql, params=()):
        try:
            return self.db.fetch_all(sql, params)
        except sqlite3.Error as exc:
            raise HeritageError(f"Could not read records: {exc}")

    def _last_id(self, table):
        rows = self._read(f"SELECT MAX(id) FROM {table}")
        return rows[0][0]

    def _check_table(self, table):
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")

    def check_description_available(self, description, exclude_id=None):
        description = clean_text(description, "Description", MAX_LONG_TEXT)
        rows = self._read("SELECT id, description FROM traditions")
        wanted = description.lower()
        for row in rows:
            if row[1].lower() == wanted and row[0] != exclude_id:
                raise HeritageError("This description is already used by another tradition.")
        return description

    def add_tradition(self, name, community, description):
        self._require(CREATE)
        name = clean_text(name, "Tradition name")
        community = clean_text(community, "Community")
        description = self.check_description_available(description)
        self._write(
            "INSERT INTO traditions (name, community, description, created_by) VALUES (?, ?, ?, ?)",
            (name, community, description, self.role),
        )
        return self._last_id(TRADITIONS)

    def add_event(self, event_name, event_date, location):
        self._require(CREATE)
        event_name = clean_text(event_name, "Event name")
        event_date = clean_date(event_date)
        location = clean_text(location, "Location")
        self._write(
            "INSERT INTO events (event_name, event_date, location, created_by) VALUES (?, ?, ?, ?)",
            (event_name, event_date, location, self.role),
        )
        return self._last_id(EVENTS)

    def list_traditions(self, keyword=None):
        self._require(READ)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            rows = self._read(
                "SELECT id, name, community, description, created_by FROM traditions "
                "WHERE name LIKE ? OR community LIKE ? ORDER BY id",
                (pattern, pattern),
            )
        else:
            rows = self._read(
                "SELECT id, name, community, description, created_by FROM traditions ORDER BY id"
            )
        records = []
        for row in rows:
            records.append(row_to_dict(TRADITION_COLUMNS, row))
        return records

    def list_events(self, keyword=None):
        self._require(READ)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            rows = self._read(
                "SELECT id, event_name, event_date, location, created_by FROM events "
                "WHERE event_name LIKE ? OR location LIKE ? ORDER BY event_date, id",
                (pattern, pattern),
            )
        else:
            rows = self._read(
                "SELECT id, event_name, event_date, location, created_by FROM events "
                "ORDER BY event_date, id"
            )
        records = []
        for row in rows:
            records.append(row_to_dict(EVENT_COLUMNS, row))
        return records

    def get_record(self, table, record_id):
        self._require(READ)
        self._check_table(table)
        record_id = clean_record_id(record_id)
        rows = self._read(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        if not rows:
            raise HeritageError(f"No record with ID {record_id} was found.")
        if table == TRADITIONS:
            return row_to_dict(TRADITION_COLUMNS, rows[0])
        return row_to_dict(EVENT_COLUMNS, rows[0])

    def update_tradition(self, record_id, name, community, description):
        self._require(UPDATE)
        self.get_record(TRADITIONS, record_id)
        record_id = clean_record_id(record_id)
        name = clean_text(name, "Tradition name")
        community = clean_text(community, "Community")
        description = self.check_description_available(description, record_id)
        self._write(
            "UPDATE traditions SET name = ?, community = ?, description = ? WHERE id = ?",
            (name, community, description, record_id),
        )

    def update_event(self, record_id, event_name, event_date, location):
        self._require(UPDATE)
        self.get_record(EVENTS, record_id)
        record_id = clean_record_id(record_id)
        event_name = clean_text(event_name, "Event name")
        event_date = clean_date(event_date)
        location = clean_text(location, "Location")
        self._write(
            "UPDATE events SET event_name = ?, event_date = ?, location = ? WHERE id = ?",
            (event_name, event_date, location, record_id),
        )

    def delete_record(self, table, record_id):
        self._require(DELETE)
        self._check_table(table)
        self.get_record(table, record_id)
        record_id = clean_record_id(record_id)
        self._write(f"DELETE FROM {table} WHERE id = ?", (record_id,))
