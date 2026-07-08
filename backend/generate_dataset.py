import pandas as pd
import random
from datetime import datetime, timedelta
import os


# -----------------------------
# Dataset Configuration
# -----------------------------

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 6, 30)

categories = {
    "Food": (500, 5000),
    "Transport": (200, 3000),
    "Shopping": (1000, 30000),
    "Bills": (1000, 15000),
    "Entertainment": (500, 10000),
    "Healthcare": (1000, 20000)
}

merchants = {
    "Food": ["KFC", "Pizza Hut", "Cafe", "Restaurant"],
    "Transport": ["Uber", "PickMe", "Bus", "Taxi"],
    "Shopping": ["Daraz", "Amazon", "Fashion Store"],
    "Bills": ["Electricity", "Water", "Internet"],
    "Entertainment": ["Netflix", "Cinema", "Gaming"],
    "Healthcare": ["Hospital", "Pharmacy"]
}

payment_methods = [
    "Cash",
    "Card",
    "Online Transfer"
]

locations = [
    "Colombo",
    "Kandy",
    "Galle",
    "Jaffna",
    "Kurunegala"
]


# -----------------------------
# Generate Transactions
# -----------------------------

transactions = []

transaction_id = 1

current_date = start_date


while current_date <= end_date:

    # Daily transaction count
    daily_transactions = random.randint(5, 10)

    for i in range(daily_transactions):

        category = random.choice(list(categories.keys()))

        amount_range = categories[category]

        amount = random.randint(
            amount_range[0],
            amount_range[1]
        )

        fraud = 0


        # Add abnormal transactions
        if random.random() < 0.05:

            amount = random.randint(50000, 300000)
            fraud = 1


        merchant = random.choice(
            merchants[category]
        )

        payment = random.choice(
            payment_methods
        )

        location = random.choice(
            locations
        )


        transactions.append([
            transaction_id,
            current_date.strftime("%Y-%m-%d"),
            amount,
            category,
            merchant,
            payment,
            location,
            fraud
        ])

        transaction_id += 1


    current_date += timedelta(days=1)



# -----------------------------
# Save Dataset
# -----------------------------

columns = [
    "transaction_id",
    "date",
    "amount",
    "category",
    "merchant",
    "payment_method",
    "location",
    "is_fraud"
]


df = pd.DataFrame(
    transactions,
    columns=columns
)


# Save to data folder

output_path = "data/transactions.csv"

df.to_csv(
    output_path,
    index=False
)


print("Dataset Generated Successfully!")
print("Total Transactions:", len(df))
print(df.head())