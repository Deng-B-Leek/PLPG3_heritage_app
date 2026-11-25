from .roles import CREATE, DELETE, READ, ROLES, UPDATE
from .services import EVENTS, TRADITIONS
from .validators import MAX_SHORT_TEXT, clean_date, clean_record_id, clean_text

DIVIDER = "-" * 70


def show_menu(role):
    print()
    print("==================== Community Culture & Heritage ====================")
    print(f"  Logged in as: {role}")
    print("  1. Add a cultural tradition")
    print("  2. Record a cultural event")
    print("  3. View saved records")
    print("  4. Search records")
    print("  5. Update a record")
    print("  6. Delete a record")
    print("  0. Exit")
    print("======================================================================")


def ask_text(prompt, field, max_length=MAX_SHORT_TEXT):
    while True:
        raw = input(prompt)
        try:
            return clean_text(raw, field, max_length)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_date(prompt):
    while True:
        raw = input(prompt)
        try:
            return clean_date(raw)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_id(prompt):
    while True:
        raw = input(prompt)
        try:
            return clean_record_id(raw)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_description(service, prompt, exclude_id=None):
    while True:
        raw = input(prompt)
        try:
            return service.check_description_available(raw, exclude_id)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_text_default(prompt, current, field, max_length=MAX_SHORT_TEXT):
    while True:
        raw = input(f"{prompt} [{current}]: ")
        if not raw.strip():
            return current
        try:
            return clean_text(raw, field, max_length)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_date_default(prompt, current):
    while True:
        raw = input(f"{prompt} [{current}]: ")
        if not raw.strip():
            return current
        try:
            return clean_date(raw)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def ask_description_default(service, prompt, current, record_id):
    while True:
        raw = input(f"{prompt} [{current}]: ")
        if not raw.strip():
            return current
        try:
            return service.check_description_available(raw, record_id)
        except ValueError as exc:
            print(f"  ! {exc} Please try again.")


def choose_role():
    print("\nWelcome to the Community Culture & Heritage Manager.")
    print("Select your role:")
    for i in range(len(ROLES)):
        print(f"  {i + 1}. {ROLES[i]}")
    while True:
        choice = input("Enter role number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ROLES):
            return ROLES[int(choice) - 1]
        print("  ! Invalid choice. Enter a number from the list.")


def pick_record_type(verb):
    print(f"\nWhich type of record do you want to {verb}?")
    print("  1. Cultural tradition")
    print("  2. Cultural event")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return TRADITIONS
        if choice == "2":
            return EVENTS
        print("  ! Please enter 1 or 2. Please try again.")


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

    def run(self):
        while True:
            show_menu(self.service.role)
            choice = input("Choose an option: ").strip()

            if choice == "0":
                print("\nThank you for preserving our culture. Goodbye!")
                return

            if choice not in ["1", "2", "3", "4", "5", "6"]:
                print("  ! Invalid choice. Please select an option from the menu.")
                continue

            try:
                self.run_option(choice)
            except ValueError as exc:
                print(f"  ! {exc}")

    def run_option(self, choice):
        if choice == "1":
            self.add_tradition()
        elif choice == "2":
            self.record_event()
        elif choice == "3":
            self.view_records()
        elif choice == "4":
            self.search_records()
        elif choice == "5":
            self.update_record()
        elif choice == "6":
            self.delete_record()

    def add_tradition(self):
        if not self.service.can(CREATE):
            raise ValueError("Your role cannot add records.")
        print("\n--- Add a cultural tradition ---")
        name = ask_text("Tradition name: ", "Tradition name")
        community = ask_text("Community: ", "Community")
        description = ask_description(self.service, "Description: ")
        record_id = self.service.add_tradition(name, community, description)
        print(f"  Saved! Tradition #{record_id} '{name}' has been recorded.")

    def record_event(self):
        if not self.service.can(CREATE):
            raise ValueError("Your role cannot add records.")
        print("\n--- Record a cultural event ---")
        event_name = ask_text("Event name: ", "Event name")
        event_date = ask_date("Event date (YYYY-MM-DD): ")
        location = ask_text("Location: ", "Location")
        record_id = self.service.add_event(event_name, event_date, location)
        print(f"  Saved! Event #{record_id} '{event_name}' has been recorded.")

    def view_records(self):
        print("\n--- Saved traditions ---")
        print_traditions(self.service.list_traditions())
        print("\n--- Saved events ---")
        print_events(self.service.list_events())

    def search_records(self):
        keyword = ask_text("Search keyword: ", "Keyword")
        print(f"\n--- Traditions matching '{keyword}' ---")
        print_traditions(self.service.list_traditions(keyword))
        print(f"\n--- Events matching '{keyword}' ---")
        print_events(self.service.list_events(keyword))

    def update_record(self):
        if not self.service.can(UPDATE):
            raise ValueError("Your role cannot update records.")
        table = pick_record_type("update")
        record_id = ask_id("Record ID to update: ")
        record = self.service.get_record(table, record_id)

        print(DIVIDER)
        print("Press Enter to keep the current value shown in brackets.")
        if table == TRADITIONS:
            name = ask_text_default("Tradition name", record["name"], "Tradition name")
            community = ask_text_default("Community", record["community"], "Community")
            description = ask_description_default(
                self.service, "Description", record["description"], record_id
            )
            self.service.update_tradition(record_id, name, community, description)
        else:
            event_name = ask_text_default("Event name", record["event_name"], "Event name")
            event_date = ask_date_default("Event date", record["event_date"])
            location = ask_text_default("Location", record["location"], "Location")
            self.service.update_event(record_id, event_name, event_date, location)
        print(f"  Record #{record_id} has been updated.")

    def delete_record(self):
        if not self.service.can(DELETE):
            raise ValueError("Your role cannot delete records.")
        table = pick_record_type("delete")
        record_id = ask_id("Record ID to delete: ")
        record = self.service.get_record(table, record_id)
        if table == TRADITIONS:
            label = record["name"]
        else:
            label = record["event_name"]

        confirm = input(f"  Type 'yes' to permanently delete '{label}': ").strip().lower()
        if confirm != "yes":
            print("  Deletion cancelled.")
            return
        self.service.delete_record(table, record_id)
        print(f"  Record #{record_id} has been deleted.")
