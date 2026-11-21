
from .errors import HeritageError, ValidationError
from .roles import Permission, Role
from .validators import MAX_LONG_TEXT, clean_date, clean_record_id, clean_text
from .services import EVENTS, TRADITIONS

MAIN_MENU = """
==================== Community Culture & Heritage ====================
  Logged in as: {role}
  1. Add a cultural tradition
  2. Record a cultural event
  3. View saved records
  4. Search records
  5. Update a record
  6. Delete a record
  0. Exit
======================================================================"""

ROLE_OPTIONS = [Role.ORGANIZER, Role.GROUP_LEADER, Role.VOLUNTEER]
DIVIDER = "-" * 70


def ask(prompt, cleaner):
    while True:
        raw = input(prompt)
        try:
            return cleaner(raw)
        except ValidationError as exc:
            print(f"  ! {exc} Please try again.")


def ask_with_default(prompt, current, cleaner):
    while True:
        raw = input(f"{prompt} [{current}]: ")
        if not raw.strip():
            return current
        try:
            return cleaner(raw)
        except ValidationError as exc:
            print(f"  ! {exc} Please try again.")


def choose_role():
    print("\nWelcome to the Community Culture & Heritage Manager.")
    print("Select your role:")
    for number, role in enumerate(ROLE_OPTIONS, start=1):
        print(f"  {number}. {role.value}")
    while True:
        choice = input("Enter role number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ROLE_OPTIONS):
            return ROLE_OPTIONS[int(choice) - 1]
        print("  ! Invalid choice. Enter a number from the list.")


def print_traditions(rows):
    if not rows:
        print("  (no traditions found)")
        return
    for row in rows:
        print(DIVIDER)
        print(f"  [Tradition #{row['id']}] {row['name']}")
        print(f"     Community   : {row['community']}")
        print(f"     Description : {row['description']}")
        print(f"     Recorded by : {row['created_by']}")


def print_events(rows):
    if not rows:
        print("  (no events found)")
        return
    for row in rows:
        print(DIVIDER)
        print(f"  [Event #{row['id']}] {row['event_name']}")
        print(f"     Date        : {row['event_date']}")
        print(f"     Location    : {row['location']}")
        print(f"     Recorded by : {row['created_by']}")


class HeritageCLI:
    def __init__(self, service):
        self.service = service
        self.actions = {
            "1": self.add_tradition,
            "2": self.record_event,
            "3": self.view_records,
            "4": self.search_records,
            "5": self.update_record,
            "6": self.delete_record,
        }

    def run(self):
        while True:
            print(MAIN_MENU.format(role=self.service.role.value))
            choice = input("Choose an option: ").strip()

            if choice == "0":
                print("\nThank you for preserving our culture. Goodbye!")
                return

            action = self.actions.get(choice)
            if action is None:
                print("  ! Invalid choice. Please select an option from the menu.")
                continue

            try:
                action()
            except HeritageError as exc:
                print(f"  ! {exc}")

    def add_tradition(self):
        if not self.service.can(Permission.CREATE):
            raise HeritageError("Your role cannot add records.")
        print("\n--- Add a cultural tradition ---")
        name = ask("Tradition name: ", lambda v: clean_text(v, "Tradition name"))
        community = ask("Community: ", lambda v: clean_text(v, "Community"))
        description = ask(
            "Description: ", lambda v: clean_text(v, "Description", MAX_LONG_TEXT)
        )
        record_id = self.service.add_tradition(name, community, description)
        print(f"  Saved! Tradition #{record_id} '{name}' has been recorded.")

    def record_event(self):
        if not self.service.can(Permission.CREATE):
            raise HeritageError("Your role cannot add records.")
        print("\n--- Record a cultural event ---")
        event_name = ask("Event name: ", lambda v: clean_text(v, "Event name"))
        event_date = ask("Event date (YYYY-MM-DD): ", clean_date)
        location = ask("Location: ", lambda v: clean_text(v, "Location"))
        record_id = self.service.add_event(event_name, event_date, location)
        print(f"  Saved! Event #{record_id} '{event_name}' has been recorded.")

    def view_records(self):
        print("\n--- Saved traditions ---")
        print_traditions(self.service.list_traditions())
        print("\n--- Saved events ---")
        print_events(self.service.list_events())

    def search_records(self):
        keyword = ask("Search keyword: ", lambda v: clean_text(v, "Keyword"))
        print(f"\n--- Traditions matching '{keyword}' ---")
        print_traditions(self.service.list_traditions(keyword))
        print(f"\n--- Events matching '{keyword}' ---")
        print_events(self.service.list_events(keyword))

    def update_record(self):
        if not self.service.can(Permission.UPDATE):
            raise HeritageError("Your role cannot update records.")
        table = self._pick_record_type("update")
        record_id = ask("Record ID to update: ", clean_record_id)
        record = self.service.get_record(table, record_id)

        print(DIVIDER)
        print("Press Enter to keep the current value shown in brackets.")
        if table == TRADITIONS:
            name = ask_with_default(
                "Tradition name", record["name"], lambda v: clean_text(v, "Tradition name")
            )
            community = ask_with_default(
                "Community", record["community"], lambda v: clean_text(v, "Community")
            )
            description = ask_with_default(
                "Description",
                record["description"],
                lambda v: clean_text(v, "Description", MAX_LONG_TEXT),
            )
            self.service.update_tradition(record_id, name, community, description)
        else:
            event_name = ask_with_default(
                "Event name", record["event_name"], lambda v: clean_text(v, "Event name")
            )
            event_date = ask_with_default("Event date", record["event_date"], clean_date)
            location = ask_with_default(
                "Location", record["location"], lambda v: clean_text(v, "Location")
            )
            self.service.update_event(record_id, event_name, event_date, location)
        print(f"  Record #{record_id} has been updated.")

    def delete_record(self):
        if not self.service.can(Permission.DELETE):
            raise HeritageError("Your role cannot delete records.")
        table = self._pick_record_type("delete")
        record_id = ask("Record ID to delete: ", clean_record_id)
        record = self.service.get_record(table, record_id)
        label = record.get("name") or record.get("event_name")

        confirm = input(f"  Type 'yes' to permanently delete '{label}': ").strip().lower()
        if confirm != "yes":
            print("  Deletion cancelled.")
            return
        self.service.delete_record(table, record_id)
        print(f"  Record #{record_id} has been deleted.")

    def _pick_record_type(self, verb):
        print(f"\nWhich type of record do you want to {verb}?")
        print("  1. Cultural tradition")
        print("  2. Cultural event")
        choice = ask(
            "Enter 1 or 2: ",
            lambda v: v.strip() if v.strip() in {"1", "2"} else _raise_invalid_choice(),
        )
        return TRADITIONS if choice == "1" else EVENTS


def _raise_invalid_choice():
    raise ValidationError("Please enter 1 or 2.")
