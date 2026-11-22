# Community Culture and Heritage Management System

A minimal, menu-driven **command-line application** written in Python that lets
community cultural organizers, cultural group leaders, and local heritage
volunteers record cultural traditions and events, search them, and keep them
up to date. Data is stored in a **SQLite** database.

Built by Group 3 for the Peer Learning Project (PLP-2), BSE Year 1, Trimester 2.

## Requirements

- Python 3.8 or newer
- No third-party packages. The app uses only the standard library (`sqlite3`).

## Running the app

```bash
python main.py
```

Choose your role at startup, then use the menu:

| Option | Action                                   | Who can use it              |
|--------|------------------------------------------|-----------------------------|
| 1      | Add a cultural tradition                 | All roles                   |
| 2      | Record a cultural event                  | All roles                   |
| 3      | View saved records                       | All roles                   |
| 4      | Search records by keyword (bonus)        | All roles                   |
| 5      | Update a record (bonus)                  | Organizer, Group Leader     |
| 6      | Delete a record (bonus)                  | Organizer, Group Leader     |
| 0      | Exit                                     | All roles                   |

To use a different database file:

```bash
HERITAGE_DB=my_archive.db python main.py
```

## Roles

| Role                          | Create | Read | Update | Delete |
|-------------------------------|:------:|:----:|:------:|:------:|
| Community Cultural Organizer  |   ✔    |  ✔   |   ✔    |   ✔    |
| Cultural Group Leader         |   ✔    |  ✔   |   ✔    |   ✔    |
| Local Heritage Volunteer      |   ✔    |  ✔   |        |        |

Each record stores the role that created it, so the database shows who recorded
what. Permissions are enforced in the service layer, not only in the menu.

## Data model

```
traditions                         events
-----------                        -----------
id           INTEGER PK            id           INTEGER PK
name         TEXT                  event_name   TEXT
community    TEXT                  event_date   TEXT  (YYYY-MM-DD)
description  TEXT                  location     TEXT
created_by   TEXT (role)           created_by   TEXT (role)
```

## Project structure

```
PLPG3_heritage_app/
├── main.py                 Entry point: opens the DB, picks a role, starts the menu
├── architecture/
│   ├── __init__.py
│   ├── database.py         SQLite connection and schema (the only DB connection code)
│   ├── services.py         Business logic: validation, permissions, CRUD queries
│   ├── validators.py       Input cleaning (text, dates, record IDs)
│   ├── roles.py            Roles and the permission matrix
│   ├── errors.py           Custom exception classes
│   └── menu.py             Terminal UI: menus, prompts, and result display
├── tests/
│   └── test_heritage.py    Unit tests (in-memory database)
├── .gitignore
└── README.md
```

### Architecture

The code is split into three layers, so each one can be changed without
rewriting the others:

1. **Interface (`menu.py`)**: prints menus, asks for input, shows results. It
   never writes SQL.
2. **Service (`services.py`, `validators.py`, `roles.py`)**: checks input and
   permissions, then calls the database. It turns database errors into
   application errors.
3. **Data (`database.py`)**: owns the connection and schema. All queries use `?`
   placeholders, so user text is never pasted into SQL. The only interpolated
   names are table names, and those are checked against a whitelist first.

## Error handling and validation

| Problem                              | What the app does                                      |
|--------------------------------------|--------------------------------------------------------|
| Invalid menu choice                  | Shows an error and returns to the menu                 |
| Empty required field                 | Explains the problem and asks again                    |
| Date not in YYYY-MM-DD format        | Explains the correct format and asks again             |
| Non-numeric or non-positive ID       | Explains the problem and asks again                    |
| Record ID that does not exist        | Shows "not found" and returns to the menu              |
| Role without permission              | Shows a permission message and returns to the menu     |
| Database error                       | Shows a message instead of crashing                    |
| Ctrl+C or end of input               | Exits cleanly                                          |

## Running the tests

From the project root:

```bash
python -m unittest discover -v
```

The tests cover input validation, record creation, search, update, delete,
missing-record errors, role permissions, and rejection of unknown table names.
They use an in-memory database, so they never touch `heritage.db`.

## Course concepts used

- **Conditionals**: menu routing, permission checks, input validation.
- **Loops**: the main menu loop and the re-prompt loops for invalid input.
- **Exception handling**: custom exceptions, `try`/`except` around database and
  input operations.
- **SQL**: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`, and `LIKE`
  search with parameterized queries.
- **Functions and modules**: each layer lives in its own module.
- **Enums**: roles and permissions.

## Team

| Member                              | Area                                |
|-------------------------------------|-------------------------------------|
| Deng Jacob Bul Leek                 | Project coordination                |
| Calvin Rugwiro                      | Research and documentation          |
| Adriel Adonijah Nakoye Mrangaye     | Terminal UI design                  |
| Davina Uwase                        | Flowchart and system design         |
| Luxe Gaultier Gayawira              | Features and database design        |
| Deng & Calvin                       | Testing and quality assurance       |
