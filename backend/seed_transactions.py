from datetime import datetime, timedelta
from transaction_store import save_transaction

# ------------------------------------------------------------
# Realistic sample transaction history for testing
# ------------------------------------------------------------

transactions = [
    # 8 weeks ago
    ("CARGILLS FOOD CITY", 4200, "30/06/2026", "Groceries"),
    ("UBER", 1450, "02/07/2026", "Transport"),

    # 7 weeks ago
    ("KEELLS SUPERMARKET", 5100, "07/07/2026", "Groceries"),
    ("DIALOG", 1800, "09/07/2026", "Utilities"),

    # 6 weeks ago
    ("CARGILLS FOOD CITY", 4600, "14/07/2026", "Groceries"),
    ("PIZZA HUT", 3200, "16/07/2026", "Food & Dining"),

    # 5 weeks ago
    ("KEELLS SUPERMARKET", 5500, "21/07/2026", "Groceries"),
    ("PICKME", 1300, "23/07/2026", "Transport"),

    # 4 weeks ago
    ("CARGILLS FOOD CITY", 4900, "28/07/2026", "Groceries"),
    ("CEB", 4200, "30/07/2026", "Utilities"),

    # 3 weeks ago
    ("KEELLS SUPERMARKET", 5800, "04/08/2026", "Groceries"),
    ("KFC", 2900, "06/08/2026", "Food & Dining"),

    # 2 weeks ago
    ("CARGILLS FOOD CITY", 5200, "11/08/2026", "Groceries"),
    ("UBER", 1700, "13/08/2026", "Transport"),

    # 1 week ago
    ("KEELLS SUPERMARKET", 6100, "18/08/2026", "Groceries"),
    ("DIALOG", 1900, "20/08/2026", "Utilities"),

    # Current week
    ("CARGILLS FOOD CITY", 5400, "24/08/2026", "Groceries"),
    ("PICKME", 1600, "24/08/2026", "Transport"),
    ("PIZZA HUT", 3500, "24/08/2026", "Food & Dining"),
    ("HEALTHGUARD PHARMACY", 2800, "24/08/2026", "Healthcare"),
]

added = 0
duplicates = 0

for merchant, amount, date, category in transactions:
    result = save_transaction(
        merchant=merchant,
        amount=amount,
        transaction_date=date,
        category=category,
        source="Seed Test Data",
        raw_ocr_text=None,
    )

    if result.get("duplicate"):
        duplicates += 1
        print(f"DUPLICATE: {merchant} | Rs. {amount} | {date}")
    else:
        added += 1
        print(f"ADDED: {merchant} | Rs. {amount} | {date}")

print("\n----------------------------------")
print(f"Added: {added}")
print(f"Duplicates skipped: {duplicates}")
print("----------------------------------")