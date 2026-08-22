import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# --------------------------------------------------
# 1. Reproducibility
# --------------------------------------------------

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


# --------------------------------------------------
# 2. Date Range
# --------------------------------------------------

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 7, 31)


# --------------------------------------------------
# 3. Categories and Merchants
# --------------------------------------------------

category_merchants = {

    "Food": [
        "KFC",
        "Pizza Hut",
        "McDonalds",
        "Keells",
        "Cargills"
    ],

    "Transport": [
        "PickMe",
        "Uber",
        "Fuel Station",
        "Bus",
        "Train"
    ],

    "Shopping": [
        "Daraz",
        "Amazon",
        "Fashion Store",
        "Supermarket"
    ],

    "Entertainment": [
        "Netflix",
        "Spotify",
        "Cinema",
        "Gaming"
    ],

    "Bills": [
        "Electricity",
        "Water",
        "Internet",
        "Mobile"
    ],

    "Health": [
        "Pharmacy",
        "Hospital",
        "Medical Centre"
    ],

    "Education": [
        "Book Shop",
        "Online Course",
        "University"
    ]
}


# --------------------------------------------------
# 4. Base Spending Profiles
# --------------------------------------------------

category_amounts = {

    "Food": (500, 5000),

    "Transport": (300, 4500),

    "Shopping": (1000, 18000),

    "Entertainment": (500, 7000),

    "Bills": (1500, 12000),

    "Health": (1000, 15000),

    "Education": (1000, 20000)
}


category_probabilities = {

    "Food": 0.28,

    "Transport": 0.20,

    "Shopping": 0.15,

    "Entertainment": 0.10,

    "Bills": 0.12,

    "Health": 0.07,

    "Education": 0.08
}


categories = list(category_probabilities.keys())

category_probs = list(category_probabilities.values())


# --------------------------------------------------
# 5. Other Transaction Features
# --------------------------------------------------

payment_methods = [
    "Cash",
    "Card",
    "Online Transfer",
    "Mobile Wallet"
]


locations = [
    "Colombo",
    "Kandy",
    "Galle",
    "Jaffna",
    "Kurunegala",
    "Anuradhapura"
]


# --------------------------------------------------
# 6. Spending Trend Function
# --------------------------------------------------

def calculate_seasonal_multiplier(date):

    multiplier = 1.0

    # Weekend spending tends to increase
    if date.weekday() >= 5:
        multiplier *= 1.12

    # December / festive season
    if date.month == 12:
        multiplier *= 1.25

    # April seasonal spending
    if date.month == 4:
        multiplier *= 1.18

    # Beginning / end of month effects
    if date.day <= 5:
        multiplier *= 1.08

    if date.day >= 25:
        multiplier *= 1.05

    # Gradual yearly spending growth
    year_growth = {
        2023: 1.00,
        2024: 1.05,
        2025: 1.10,
        2026: 1.15
    }

    multiplier *= year_growth.get(
        date.year,
        1.0
    )

    return multiplier


# --------------------------------------------------
# 7. Fraud Generator
# --------------------------------------------------

def generate_fraud_label(
    amount,
    payment_method,
    category
):

    fraud_probability = 0.015

    # Large transaction
    if amount > 25000:
        fraud_probability += 0.08

    if amount > 40000:
        fraud_probability += 0.15

    # Online transfer
    if payment_method == "Online Transfer":
        fraud_probability += 0.025

    # Shopping risk
    if category == "Shopping":
        fraud_probability += 0.015

    return int(
        random.random()
        < fraud_probability
    )


# --------------------------------------------------
# 8. Generate Transactions
# --------------------------------------------------

transactions = []

transaction_id = 1

current_date = START_DATE


while current_date <= END_DATE:

    # Normal number of transactions per day
    base_transactions = np.random.poisson(
        lam=4
    )

    # More activity on weekends
    if current_date.weekday() >= 5:
        base_transactions += np.random.randint(
            0,
            3
        )

    # Generate normal transactions
    for _ in range(base_transactions):

        category = np.random.choice(
            categories,
            p=category_probs
        )

        merchant = random.choice(
            category_merchants[category]
        )

        min_amount, max_amount = (
            category_amounts[category]
        )

        # Generate realistic amount
        amount = np.random.lognormal(
            mean=np.log(
                (min_amount + max_amount) / 3
            ),
            sigma=0.55
        )

        amount = max(
            min_amount,
            min(
                amount,
                max_amount
            )
        )

        # Seasonal behaviour
        amount *= calculate_seasonal_multiplier(
            current_date
        )

        # Random natural variation
        amount *= np.random.uniform(
            0.90,
            1.10
        )

        amount = round(amount, 2)

        payment_method = random.choice(
            payment_methods
        )

        location = random.choice(
            locations
        )

        is_fraud = generate_fraud_label(
            amount,
            payment_method,
            category
        )

        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                current_date.strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                amount,

            "category":
                category,

            "merchant":
                merchant,

            "payment_method":
                payment_method,

            "location":
                location,

            "is_fraud":
                is_fraud
        })

        transaction_id += 1


    # --------------------------------------------------
    # 9. Recurring Monthly Transactions
    # --------------------------------------------------

    # Internet subscription
    if current_date.day == 5:

        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                current_date.strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                round(
                    3500
                    * calculate_seasonal_multiplier(
                        current_date
                    ),
                    2
                ),

            "category":
                "Bills",

            "merchant":
                "Internet",

            "payment_method":
                "Online Transfer",

            "location":
                "Colombo",

            "is_fraud":
                0
        })

        transaction_id += 1


    # Netflix recurring payment
    if current_date.day == 10:

        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                current_date.strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                3200,

            "category":
                "Entertainment",

            "merchant":
                "Netflix",

            "payment_method":
                "Card",

            "location":
                "Colombo",

            "is_fraud":
                0
        })

        transaction_id += 1


    # Electricity bill
    if current_date.day == 20:

        electricity_amount = np.random.normal(
            6500,
            900
        )

        electricity_amount = max(
            electricity_amount,
            3000
        )

        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                current_date.strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                round(
                    electricity_amount,
                    2
                ),

            "category":
                "Bills",

            "merchant":
                "Electricity",

            "payment_method":
                "Online Transfer",

            "location":
                "Colombo",

            "is_fraud":
                0
        })

        transaction_id += 1


    current_date += timedelta(days=1)


# --------------------------------------------------
# 10. Create DataFrame
# --------------------------------------------------

data = pd.DataFrame(
    transactions
)


# --------------------------------------------------
# 11. Sort Dataset
# --------------------------------------------------

data["date"] = pd.to_datetime(
    data["date"]
)

data = data.sort_values(
    "date"
).reset_index(drop=True)

data["transaction_id"] = (
    range(
        1,
        len(data) + 1
    )
)


# --------------------------------------------------
# 12. Save Dataset
# --------------------------------------------------

os.makedirs(
    "data",
    exist_ok=True
)

output_path = (
    "data/transactions.csv"
)

data.to_csv(
    output_path,
    index=False
)


# --------------------------------------------------
# 13. Display Results
# --------------------------------------------------

print(
    "Long-Term Financial Dataset "
    "Generated Successfully!"
)

print(
    "\nTotal Transactions:",
    len(data)
)

print(
    "Start Date:",
    data["date"].min().date()
)

print(
    "End Date:",
    data["date"].max().date()
)

print(
    "\nFraud Distribution:"
)

print(
    data["is_fraud"].value_counts()
)

print(
    "\nFraud Percentage:"
)

print(
    round(
        data["is_fraud"].mean()
        * 100,
        2
    ),
    "%"
)

print(
    "\nCategory Distribution:"
)

print(
    data["category"].value_counts()
)

print(
    "\nSample Data:"
)

print(
    data.head()
)

print(
    "\nDataset Saved To:",
    output_path
)