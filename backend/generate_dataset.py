import pandas as pd
import random
import os
from datetime import datetime, timedelta


# -------------------------------
# Settings
# -------------------------------

number_of_transactions = 3000

output_file = "data/transactions.csv"


# -------------------------------
# Dataset Values
# -------------------------------

categories = {
    "Food": {
        "merchants": [
            "KFC",
            "Pizza Hut",
            "Restaurant",
            "Cafe"
        ],
        "amount": (500, 8000)
    },

    "Shopping": {
        "merchants": [
            "Amazon",
            "Daraz",
            "Fashion Store",
            "Supermarket"
        ],
        "amount": (5000, 60000)
    },

    "Healthcare": {
        "merchants": [
            "Hospital",
            "Pharmacy",
            "Medical Center"
        ],
        "amount": (3000, 40000)
    },

    "Transport": {
        "merchants": [
            "Uber",
            "PickMe",
            "Bus",
            "Taxi"
        ],
        "amount": (200, 8000)
    },

    "Entertainment": {
        "merchants": [
            "Netflix",
            "Cinema",
            "Gaming"
        ],
        "amount": (1000, 20000)
    },

    "Bills": {
        "merchants": [
            "Electricity",
            "Water",
            "Internet"
        ],
        "amount": (1000, 25000)
    }
}


payment_methods = [
    "Cash",
    "Card",
    "Online Transfer"
]


locations = [
    "Colombo",
    "Kandy",
    "Jaffna",
    "Galle",
    "Kurunegala"
]


# -------------------------------
# Generate Dates
# -------------------------------

start_date = datetime(2026,1,1)


data = []


# -------------------------------
# Create Transactions
# -------------------------------

for i in range(1, number_of_transactions + 1):

    category = random.choice(
        list(categories.keys())
    )


    merchant = random.choice(
        categories[category]["merchants"]
    )


    min_amount, max_amount = categories[category]["amount"]


    amount = random.randint(
        min_amount,
        max_amount
    )


    payment_method = random.choice(
        payment_methods
    )


    location = random.choice(
        locations
    )


    transaction_date = (
        start_date +
        timedelta(
            days=random.randint(0,179)
        )
    )


    # -------------------------------
    # Fraud Logic
    # -------------------------------

    fraud_probability = 0.03


    if amount > 40000:
        fraud_probability = 0.25


    if payment_method == "Online Transfer":
        fraud_probability += 0.05


    is_fraud = (
        1
        if random.random() < fraud_probability
        else 0
    )


    data.append({

        "transaction_id": i,

        "date": transaction_date.strftime(
            "%Y-%m-%d"
        ),

        "amount": amount,

        "category": category,

        "merchant": merchant,

        "payment_method": payment_method,

        "location": location,

        "is_fraud": is_fraud

    })


# -------------------------------
# Save Dataset
# -------------------------------

df = pd.DataFrame(data)


if not os.path.exists("data"):
    os.makedirs("data")


df.to_csv(
    output_file,
    index=False
)


print("Dataset Generated Successfully!")
print("Total Transactions:", len(df))

print("\nSample Data:")
print(df.head())