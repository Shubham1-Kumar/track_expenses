import os
import sqlite3

from werkzeug.security import generate_password_hash

# Path to the SQLite file. Defaults to <project_root>/expense_tracker.db.
# Overridable via the SPENDLY_DB_PATH env var so tests can point at a temp file.
_DEFAULT_DB_NAME = "expense_tracker.db"
DB_PATH = os.environ.get(
    "SPENDLY_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), _DEFAULT_DB_NAME),
)

# Fixed category list (spec §10). Kept here so future steps can import it
# instead of hardcoding the same strings in templates/routes.
CATEGORIES = (
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
)


def get_db():
    """Open a SQLite connection with dict-like rows and FK enforcement on."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    # FKs are off by default in SQLite — must be set per-connection (CLAUDE.md).
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db():
    """Create the users and expenses tables. Safe to call repeatedly."""
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    connection = get_db()
    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


def seed_db():
    """Insert one demo user and 8 sample expenses — only if users is empty.

    Idempotent: returns early when users already has data so the seed never
    duplicates records across app restarts.
    """
    connection = get_db()
    try:
        existing = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        # 8 expenses spread across June 2026, covering all 7 fixed categories.
        # Food appears twice so the count of 8 lands without dropping a category.
        expenses = [
            (user_id, 350.00, "Food",          "2026-06-01", "Groceries"),
            (user_id, 180.00, "Food",          "2026-06-03", "Lunch at office"),
            (user_id, 120.00, "Transport",     "2026-06-05", "Uber to airport"),
            (user_id, 1500.00, "Bills",        "2026-06-08", "Electricity bill"),
            (user_id, 450.00, "Health",        "2026-06-10", "Pharmacy"),
            (user_id, 600.00, "Entertainment", "2026-06-12", "Movie night"),
            (user_id, 1200.00, "Shopping",     "2026-06-13", "New shoes"),
            (user_id, 80.00, "Transport",      "2026-06-14", "Metro pass"),
        ]
        connection.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            expenses,
        )
        connection.commit()
    finally:
        connection.close()
