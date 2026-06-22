"""Seed <count> realistic expenses for a given user, spread across the past <months> months.

Usage: python seed_expenses.py <user_id> <count> <months>
Example: python seed_expenses.py 1 50 6
"""

import random
import sys
from datetime import datetime, timedelta

from database.db import CATEGORIES, get_db

# Weighted distribution: Food most common, Health & Entertainment least.
# Weights sum to 100 — picked to match the spec's "roughly proportional" guidance.
CATEGORY_WEIGHTS = {
    "Food":          30,
    "Transport":     18,
    "Shopping":      15,
    "Bills":         12,
    "Other":         12,
    "Health":         7,
    "Entertainment":  6,
}

# Realistic Indian-context descriptions per category.
DESCRIPTIONS = {
    "Food": [
        "Chai and samosa",
        "Lunch at office canteen",
        "Dinner at Haldiram's",
        "Groceries from D-Mart",
        "Swiggy order",
        "Zomato dinner",
        "Breakfast at Indian Coffee House",
        "Street food - pav bhaji",
        "BigBasket groceries",
        "Dominos pizza",
    ],
    "Transport": [
        "Uber to airport",
        "Auto rickshaw",
        "Ola cab",
        "Metro pass recharge",
        "Petrol refill",
        "Rapido bike ride",
        "Train ticket",
        "BMTC bus pass",
    ],
    "Bills": [
        "Electricity bill",
        "Mobile recharge",
        "Broadband bill",
        "Gas cylinder refill",
        "Water bill",
        "Credit card bill",
        "DTH recharge",
    ],
    "Health": [
        "Pharmacy medicines",
        "Doctor consultation",
        "Lab tests",
        "Gym membership",
        "Health supplements",
        "Dental checkup",
    ],
    "Entertainment": [
        "Movie tickets - PVR",
        "Netflix subscription",
        "Spotify Premium",
        "Bookstore purchase",
        "Amusement park ticket",
        "Concert ticket",
    ],
    "Shopping": [
        "New shoes - Nike",
        "Amazon order",
        "Flipkart purchase",
        "Clothing from Myntra",
        "Electronics from Croma",
        "Home decor",
        "Gift for friend",
    ],
    "Other": [
        "Birthday gift",
        "Charity donation",
        "Haircut",
        "Stationery",
        "Courier charges",
        "Parking fee",
    ],
}

# Min/max amount ranges per category (in ₹).
AMOUNT_RANGES = {
    "Food":          (50,   800),
    "Transport":     (20,   500),
    "Bills":         (200,  3000),
    "Health":        (100,  2000),
    "Entertainment": (100,  1500),
    "Shopping":      (200,  5000),
    "Other":         (50,   1000),
}


def parse_args(argv):
    """Return (user_id, count, months) or None if args are invalid."""
    if len(argv) != 4:
        return None
    try:
        user_id = int(argv[1])
        count = int(argv[2])
        months = int(argv[3])
        if user_id <= 0 or count <= 0 or months <= 0:
            return None
        return user_id, count, months
    except ValueError:
        return None


def weighted_category():
    """Pick a category respecting the weighted distribution."""
    categories = list(CATEGORY_WEIGHTS.keys())
    weights = list(CATEGORY_WEIGHTS.values())
    return random.choices(categories, weights=weights, k=1)[0]


def random_date_in_window(months: int) -> datetime:
    """Random datetime between (today - months) and today, inclusive of both ends."""
    now = datetime.now()
    earliest = now - timedelta(days=months * 30)  # approximate month length
    delta_seconds = int((now - earliest).total_seconds())
    return earliest + timedelta(seconds=random.randint(0, delta_seconds))


def main():
    parsed = parse_args(sys.argv)
    if parsed is None:
        print("Usage: python seed_expenses.py <user_id> <count> <months>")
        print("Example: python seed_expenses.py 1 50 6")
        sys.exit(1)

    user_id, count, months = parsed

    connection = get_db()
    try:
        # Step 2: verify the user exists.
        user_row = connection.execute(
            "SELECT id, name FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user_row is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        # Step 3: generate and insert expenses in a single transaction.
        # Capture the date range and a sample as we go so Step 4 can print them
        # even if something downstream fails before commit.
        random.seed()  # use system entropy
        rows = []
        for _ in range(count):
            category = weighted_category()
            low, high = AMOUNT_RANGES[category]
            amount = round(random.uniform(low, high), 2)
            description = random.choice(DESCRIPTIONS[category])
            date_obj = random_date_in_window(months)
            rows.append(
                (user_id, amount, category, date_obj.strftime("%Y-%m-%d"), description)
            )

        try:
            connection.executemany(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Insert failed, all changes rolled back: {e}")
            sys.exit(1)

        # Step 4: report results.
        dates = [r[3] for r in rows]
        print(f"Inserted {len(rows)} expenses for user '{user_row['name']}' (id={user_id}).")
        print(f"Date range: {min(dates)}  to  {max(dates)}")
        print("\nSample of 5 inserted records:")
        print(f"  {'ID':<4} {'Date':<12} {'Category':<14} {'Amount':>8}  Description")
        for r in random.sample(rows, k=5):
            amount, category, date_str, description = r[1], r[2], r[3], r[4]
            print(f"  {'-':<4} {date_str:<12} {category:<14} ₹{amount:>7.2f}  {description}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
