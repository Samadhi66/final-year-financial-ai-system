import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta


# ============================================================
# 1. SETTINGS
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 7, 31)

# Normal weekly spending level
BASE_WEEKLY_SPENDING = 150000


# ============================================================
# 2. CATEGORY INFORMATION
# ============================================================

CATEGORY_RATIOS = {
    "Food": 0.25,
    "Transport": 0.15,
    "Shopping": 0.15,
    "Entertainment": 0.08,
    "Bills": 0.20,
    "Health": 0.07,
    "Education": 0.10
}


CATEGORY_MERCHANTS = {

    "Food": [
        "Keells",
        "Cargills",
        "KFC",
        "Pizza Hut",
        "Restaurant"
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
        "Fashion Store",
        "Supermarket",
        "Electronics Store"
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


PAYMENT_METHODS = [
    "Cash",
    "Card",
    "Online Transfer",
    "Mobile Wallet"
]


LOCATIONS = [
    "Colombo",
    "Kandy",
    "Galle",
    "Jaffna",
    "Kurunegala",
    "Anuradhapura"
]


# ============================================================
# 3. LONG-TERM SPENDING TREND
# ============================================================

def get_year_multiplier(year):

    values = {
        2023: 1.00,
        2024: 1.05,
        2025: 1.10,
        2026: 1.15
    }

    return values.get(year, 1.0)


# ============================================================
# 4. SEASONAL SPENDING
# ============================================================

def get_seasonal_multiplier(date):

    multiplier = 1.0

    # January slightly lower
    if date.month == 1:
        multiplier *= 0.95

    # April New Year period
    if date.month == 4:
        multiplier *= 1.15

    # December festive period
    if date.month == 12:
        multiplier *= 1.20

    return multiplier


# ============================================================
# 5. MONTHLY PAY-CYCLE BEHAVIOUR
# ============================================================

def get_pay_cycle_multiplier(date):

    day = date.day

    # Salary period / beginning of month
    if day <= 7:
        return 1.08

    # Middle of month
    elif day <= 14:
        return 1.02

    elif day <= 21:
        return 0.97

    # End of month
    else:
        return 0.94


# ============================================================
# 6. FRAUD LABEL
# ============================================================

def create_fraud_label(
    amount,
    expected_amount,
    payment_method
):

    probability = 0.01

    # Large behavioural deviation
    if amount > expected_amount * 1.8:
        probability += 0.08

    if amount > expected_amount * 2.5:
        probability += 0.15

    # Online transfer slightly higher risk
    if payment_method == "Online Transfer":
        probability += 0.02

    return int(
        random.random() < probability
    )


# ============================================================
# 7. GENERATE WEEKLY FINANCIAL BEHAVIOUR
# ============================================================

weekly_profiles = []

week_start = START_DATE

previous_week_spending = BASE_WEEKLY_SPENDING


while week_start <= END_DATE:

    year_effect = get_year_multiplier(
        week_start.year
    )

    seasonal_effect = get_seasonal_multiplier(
        week_start
    )

    pay_cycle_effect = get_pay_cycle_multiplier(
        week_start
    )


    # --------------------------------------------------------
    # Stable baseline spending level
    # --------------------------------------------------------

    baseline = (
        BASE_WEEKLY_SPENDING
        * year_effect
        * seasonal_effect
        * pay_cycle_effect
    )


    # --------------------------------------------------------
    # Autoregressive behaviour
    #
    # 75% influenced by previous spending
    # 25% influenced by expected baseline
    #
    # This creates realistic spending continuity.
    # --------------------------------------------------------

    weekly_spending = (
        previous_week_spending * 0.75
        +
        baseline * 0.25
    )


    # --------------------------------------------------------
    # Small natural variation
    # --------------------------------------------------------

    weekly_spending *= np.random.normal(
        loc=1.0,
        scale=0.02
    )


    # --------------------------------------------------------
    # Occasional legitimate spending spike
    # --------------------------------------------------------

    if random.random() < 0.025:

        weekly_spending *= np.random.uniform(
            1.08,
            1.18
        )


    weekly_spending = max(
        weekly_spending,
        85000
    )


    weekly_profiles.append({

        "week_start":
            week_start,

        "weekly_spending":
            round(
                weekly_spending,
                2
            )
    })


    previous_week_spending = (
        weekly_spending
    )


    week_start += timedelta(
        days=7
    )


# ============================================================
# 8. GENERATE TRANSACTIONS
# ============================================================

transactions = []

transaction_id = 1


for profile in weekly_profiles:

    week_start = profile[
        "week_start"
    ]

    weekly_target = profile[
        "weekly_spending"
    ]


    # --------------------------------------------------------
    # 8.1 Fixed recurring payments for the week
    # --------------------------------------------------------

    recurring_transactions = []


    # Internet Bill
    if week_start.day <= 7:

        recurring_transactions.append({
            "date": week_start,
            "amount": 4500,
            "category": "Bills",
            "merchant": "Internet",
            "payment_method": "Online Transfer",
            "location": "Colombo"
        })


    # Netflix
    if 8 <= week_start.day <= 14:

        recurring_transactions.append({
            "date": week_start,
            "amount": 3000,
            "category": "Entertainment",
            "merchant": "Netflix",
            "payment_method": "Card",
            "location": "Colombo"
        })


    # Electricity Bill
    if 15 <= week_start.day <= 21:

        electricity = max(
            np.random.normal(
                7000
                * get_year_multiplier(
                    week_start.year
                ),
                500
            ),
            3500
        )

        recurring_transactions.append({
            "date": week_start,
            "amount": round(
                electricity,
                2
            ),
            "category": "Bills",
            "merchant": "Electricity",
            "payment_method": "Online Transfer",
            "location": "Colombo"
        })


    recurring_total = sum(
        item["amount"]
        for item
        in recurring_transactions
    )


    # Remaining budget available for normal transactions
    discretionary_target = max(
        weekly_target
        - recurring_total,
        weekly_target * 0.75
    )


    # --------------------------------------------------------
    # 8.2 Number of normal transactions
    # --------------------------------------------------------

    transaction_count = int(
        np.clip(
            np.random.normal(
                loc=30,
                scale=3
            ),
            22,
            38
        )
    )


    raw_transactions = []


    # --------------------------------------------------------
    # 8.3 Generate raw transaction weights
    # --------------------------------------------------------

    for _ in range(
        transaction_count
    ):

        category = random.choices(

            population=list(
                CATEGORY_RATIOS.keys()
            ),

            weights=list(
                CATEGORY_RATIOS.values()
            ),

            k=1

        )[0]


        transaction_date = (
            week_start
            + timedelta(
                days=random.randint(
                    0,
                    6
                )
            )
        )


        if transaction_date > END_DATE:
            continue


        merchant = random.choice(
            CATEGORY_MERCHANTS[
                category
            ]
        )


        payment_method = random.choice(
            PAYMENT_METHODS
        )


        location = random.choice(
            LOCATIONS
        )


        # Category behaviour
        category_weight = (
            CATEGORY_RATIOS[
                category
            ]
        )


        # Natural transaction-size variation
        random_weight = np.random.lognormal(
            mean=0,
            sigma=0.25
        )


        raw_weight = (
            category_weight
            * random_weight
        )


        # Weekend transactions often larger
        if transaction_date.weekday() >= 5:

            raw_weight *= 1.08


        raw_transactions.append({

            "date":
                transaction_date,

            "category":
                category,

            "merchant":
                merchant,

            "payment_method":
                payment_method,

            "location":
                location,

            "raw_weight":
                raw_weight
        })


    # --------------------------------------------------------
    # 8.4 NORMALIZE TRANSACTIONS
    #
    # Total transaction amounts are scaled to match the
    # weekly behavioural spending target.
    # --------------------------------------------------------

    total_raw_weight = sum(

        item["raw_weight"]

        for item in raw_transactions
    )


    if total_raw_weight == 0:
        total_raw_weight = 1


    for item in raw_transactions:

        amount = (

            item["raw_weight"]
            /
            total_raw_weight
            *
            discretionary_target

        )


        amount = max(
            amount,
            100
        )


        amount = round(
            amount,
            2
        )


        expected_amount = (
            discretionary_target
            /
            max(
                len(
                    raw_transactions
                ),
                1
            )
        )


        is_fraud = create_fraud_label(

            amount,
            expected_amount,
            item[
                "payment_method"
            ]
        )


        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                item["date"]
                .strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                amount,

            "category":
                item[
                    "category"
                ],

            "merchant":
                item[
                    "merchant"
                ],

            "payment_method":
                item[
                    "payment_method"
                ],

            "location":
                item[
                    "location"
                ],

            "is_fraud":
                is_fraud
        })


        transaction_id += 1


    # --------------------------------------------------------
    # 8.5 Add recurring transactions
    # --------------------------------------------------------

    for item in recurring_transactions:

        transactions.append({

            "transaction_id":
                transaction_id,

            "date":
                item["date"]
                .strftime(
                    "%Y-%m-%d"
                ),

            "amount":
                round(
                    item["amount"],
                    2
                ),

            "category":
                item[
                    "category"
                ],

            "merchant":
                item[
                    "merchant"
                ],

            "payment_method":
                item[
                    "payment_method"
                ],

            "location":
                item[
                    "location"
                ],

            "is_fraud":
                0
        })


        transaction_id += 1


# ============================================================
# 9. CREATE FINAL DATAFRAME
# ============================================================

data = pd.DataFrame(
    transactions
)


data["date"] = pd.to_datetime(
    data["date"]
)


data = data.sort_values(
    "date"
).reset_index(
    drop=True
)


data["transaction_id"] = range(
    1,
    len(data) + 1
)


# ============================================================
# 10. SAVE DATASET
# ============================================================

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


# ============================================================
# 11. SUMMARY
# ============================================================

print(
    "Final Behaviour-Based Financial Dataset "
    "Generated Successfully!"
)


print(
    "\nTotal Transactions:",
    len(data)
)


print(
    "Start Date:",
    data["date"]
    .min()
    .date()
)


print(
    "End Date:",
    data["date"]
    .max()
    .date()
)


print(
    "\nAverage Transaction Amount:",
    round(
        data["amount"]
        .mean(),
        2
    )
)


print(
    "\nFraud Distribution:"
)


print(
    data[
        "is_fraud"
    ].value_counts()
)


print(
    "\nFraud Percentage:",
    round(
        data[
            "is_fraud"
        ].mean()
        * 100,
        2
    ),
    "%"
)


print(
    "\nDataset Saved To:",
    output_path
)