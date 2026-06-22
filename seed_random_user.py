"""One-off script to seed a single random Indian user into the Spendly DB.

Reuses the same get_db() helper and connection pattern as database/db.py so
behaviour matches what the app would do at runtime.
"""

import os
import random
import sys

# Make `database` importable when running from the project root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash

from database.db import get_db

# Common Indian first + last names spanning regions (North, South, East, West).
# Intentionally not exhaustive — just a realistic spread.
FIRST_NAMES = [
    # North
    "Rahul", "Amit", "Priya", "Neha", "Vikram", "Anjali", "Rohit", "Pooja",
    "Karan", "Sneha",
    # South
    "Arjun", "Kavya", "Ravi", "Deepa", "Karthik", "Meena", "Suresh", "Lakshmi",
    "Vijay", "Anitha",
    # East
    "Suman", "Ritesh", "Pallavi", "Bibek", "Ananya", "Manish",
    # West
    "Nikhil", "Isha", "Hardik", "Mira", "Yash", "Rhea",
]

LAST_NAMES = [
    # North
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Agarwal", "Jain", "Mishra",
    "Saxena", "Kapoor",
    # South
    "Reddy", "Iyer", "Nair", "Pillai", "Rao", "Menon", "Krishnan", "Bhat",
    # East
    "Mukherjee", "Chatterjee", "Banerjee", "Das", "Sen", "Ghosh",
    # West
    "Shah", "Desai", "Mehta", "Joshi", "Kulkarni", "Deshmukh",
]


def random_email(name: str) -> str:
    first, last = name.lower().split()
    suffix = random.randint(10, 999)  # 2-3 digit numeric tail
    return f"{first}.{last}{suffix}@gmail.com"


def email_exists(connection, email: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,)
    ).fetchone()
    return row is not None


def main() -> None:
    connection = get_db()
    try:
        # Loop until we find a name whose derived email is not already taken.
        # Bound the loop so a freakishly full DB can't hang the script.
        for _ in range(1000):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = random_email(name)
            if not email_exists(connection, email):
                break
        else:
            raise RuntimeError("Could not find a unique email after 1000 attempts")

        cursor = connection.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash("password123")),
        )
        connection.commit()
        user_id = cursor.lastrowid

        print(f"id: {user_id}")
        print(f"name: {name}")
        print(f"email: {email}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
