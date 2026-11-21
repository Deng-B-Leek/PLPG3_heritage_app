
import unittest

from architecture.database import Database
from architecture.errors import PermissionDenied, RecordNotFound, ValidationError
from architecture.roles import Role
from architecture.services import EVENTS, TRADITIONS, HeritageService
from architecture.validators import clean_date, clean_record_id, clean_text


class ValidatorTests(unittest.TestCase):
    def test_clean_text_strips_extra_spaces(self):
        self.assertEqual(clean_text("  Kinyarwanda   drums ", "Name"), "Kinyarwanda drums")

    def test_clean_text_rejects_empty(self):
        with self.assertRaises(ValidationError):
            clean_text("   ", "Name")

    def test_clean_text_rejects_none(self):
        with self.assertRaises(ValidationError):
            clean_text(None, "Name")

    def test_clean_text_enforces_length(self):
        with self.assertRaises(ValidationError):
            clean_text("x" * 121, "Name")

    def test_clean_date_accepts_iso_format(self):
        self.assertEqual(clean_date("2026-12-05"), "2026-12-05")

    def test_clean_date_rejects_wrong_format(self):
        for bad in ["05/12/2026", "2026-13-01", "not a date", ""]:
            with self.subTest(value=bad), self.assertRaises(ValidationError):
                clean_date(bad)

    def test_clean_record_id(self):
        self.assertEqual(clean_record_id(" 7 "), 7)
        for bad in ["abc", "0", "-3", ""]:
            with self.subTest(value=bad), self.assertRaises(ValidationError):
                clean_record_id(bad)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.organizer = HeritageService(self.db, Role.ORGANIZER)
        self.volunteer = HeritageService(self.db, Role.VOLUNTEER)

    def tearDown(self):
        self.db.close()

    def test_add_tradition_saves_record_with_role(self):
        new_id = self.organizer.add_tradition("Umuganura", "Rwandan farmers", "Harvest festival")
        rows = self.organizer.list_traditions()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], new_id)
        self.assertEqual(rows[0]["created_by"], Role.ORGANIZER.value)

    def test_add_event_saves_record(self):
        new_id = self.organizer.add_event("Film Night", "2026-12-01", "Kigali")
        rows = self.organizer.list_events()
        self.assertEqual(rows[0]["id"], new_id)
        self.assertEqual(rows[0]["event_date"], "2026-12-01")

    def test_invalid_event_date_is_not_saved(self):
        with self.assertRaises(ValidationError):
            self.organizer.add_event("Film Night", "01-12-2026", "Kigali")
        self.assertEqual(self.organizer.list_events(), [])

    def test_volunteer_can_create_records(self):
        self.volunteer.add_tradition("Intore dance", "Youth group", "Traditional dance")
        self.assertEqual(len(self.volunteer.list_traditions()), 1)

    def test_search_matches_name_or_community(self):
        self.organizer.add_tradition("Umuganura", "Rwandan farmers", "Harvest festival")
        self.organizer.add_tradition("Igisoro", "Village elders", "Board game")
        self.assertEqual(len(self.organizer.list_traditions("umu")), 1)
        self.assertEqual(len(self.organizer.list_traditions("elders")), 1)
        self.assertEqual(len(self.organizer.list_traditions("nothing")), 0)

    def test_get_record_missing_raises(self):
        with self.assertRaises(RecordNotFound):
            self.organizer.get_record(TRADITIONS, 999)

    def test_update_tradition(self):
        record_id = self.organizer.add_tradition("Old name", "Community", "Desc")
        self.organizer.update_tradition(record_id, "New name", "Community", "Desc")
        self.assertEqual(self.organizer.get_record(TRADITIONS, record_id)["name"], "New name")

    def test_update_event(self):
        record_id = self.organizer.add_event("Concert", "2026-12-01", "Kigali")
        self.organizer.update_event(record_id, "Concert", "2026-12-15", "Musanze")
        row = self.organizer.get_record(EVENTS, record_id)
        self.assertEqual(row["event_date"], "2026-12-15")
        self.assertEqual(row["location"], "Musanze")

    def test_volunteer_cannot_update(self):
        record_id = self.organizer.add_tradition("Name", "Community", "Desc")
        with self.assertRaises(PermissionDenied):
            self.volunteer.update_tradition(record_id, "Changed", "Community", "Desc")

    def test_delete_record(self):
        record_id = self.organizer.add_event("Concert", "2026-12-01", "Kigali")
        self.organizer.delete_record(EVENTS, record_id)
        self.assertEqual(self.organizer.list_events(), [])

    def test_delete_missing_record_raises(self):
        with self.assertRaises(RecordNotFound):
            self.organizer.delete_record(EVENTS, 42)

    def test_volunteer_cannot_delete(self):
        record_id = self.organizer.add_event("Concert", "2026-12-01", "Kigali")
        with self.assertRaises(PermissionDenied):
            self.volunteer.delete_record(EVENTS, record_id)
        self.assertEqual(len(self.organizer.list_events()), 1)

    def test_unknown_table_is_rejected(self):
        with self.assertRaises(ValueError):
            self.organizer.delete_record("users; DROP TABLE events", 1)


if __name__ == "__main__":
    unittest.main()
