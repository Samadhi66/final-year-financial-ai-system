import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. Load Transaction Dataset
# --------------------------------------------------

data = pd.read_csv(
    "data/transactions.csv"
)

print("Original Dataset Loaded")
print("Original Shape:", data.shape)


# --------------------------------------------------
# 2. Convert Date Column
# --------------------------------------------------

data["date"] = pd.to_datetime(
    data["date"]
)

data = data.sort_values(
    "date"
).reset_index(drop=True)


# --------------------------------------------------
# 3. Aggregate Using Generator-Aligned Weeks
# --------------------------------------------------
# The synthetic generator creates weeks as:
# Sunday -> Saturday.
#
# W-SAT keeps the aggregation aligned with that
# behavioural week instead of ISO Monday-Sunday weeks.

weekly = (

    data.set_index("date")

    .resample("W-SAT")

    .agg(

        weekly_spending=(
            "amount",
            "sum"
        ),

        avg_transaction_amount=(
            "amount",
            "mean"
        ),

        transaction_count=(
            "transaction_id",
            "count"
        ),

        fraud_count=(
            "is_fraud",
            "sum"
        )
    )

    .reset_index()
)


weekly = weekly.rename(
    columns={
        "date": "week_end"
    }
)


# Remove any empty weeks
weekly = weekly[
    weekly["transaction_count"] > 0
].reset_index(drop=True)


print("\nWeekly Aggregation Completed")
print("Weekly Records:", len(weekly))


# --------------------------------------------------
# 4. Calendar / Seasonal Features
# --------------------------------------------------

weekly["year"] = (
    weekly["week_end"].dt.year
)

weekly["month"] = (
    weekly["week_end"].dt.month
)

weekly["week_of_year"] = (
    weekly["week_end"]
    .dt.isocalendar()
    .week
    .astype(int)
)


# Cyclical week features
weekly["week_sin"] = np.sin(
    2 * np.pi
    * weekly["week_of_year"]
    / 52
)

weekly["week_cos"] = np.cos(
    2 * np.pi
    * weekly["week_of_year"]
    / 52
)


# --------------------------------------------------
# 5. Historical Spending Features
# --------------------------------------------------
# IMPORTANT:
# We are predicting NEXT week.
#
# Therefore CURRENT week's spending is valid
# historical information and is NOT target leakage.

weekly["current_week_spending"] = (
    weekly["weekly_spending"]
)


weekly["spending_1_week_ago"] = (
    weekly["weekly_spending"]
    .shift(1)
)


weekly["spending_2_weeks_ago"] = (
    weekly["weekly_spending"]
    .shift(2)
)


weekly["spending_3_weeks_ago"] = (
    weekly["weekly_spending"]
    .shift(3)
)


weekly["spending_4_weeks_ago"] = (
    weekly["weekly_spending"]
    .shift(4)
)


# --------------------------------------------------
# 6. Rolling Spending Features
# --------------------------------------------------

weekly["previous_2_week_avg"] = (

    weekly["weekly_spending"]

    .rolling(window=2)

    .mean()
)


weekly["previous_4_week_avg"] = (

    weekly["weekly_spending"]

    .rolling(window=4)

    .mean()
)


weekly["previous_8_week_avg"] = (

    weekly["weekly_spending"]

    .rolling(window=8)

    .mean()
)


# --------------------------------------------------
# 7. Current Behaviour Features
# --------------------------------------------------

weekly["current_transaction_count"] = (
    weekly["transaction_count"]
)


weekly["current_avg_transaction_amount"] = (
    weekly["avg_transaction_amount"]
)


weekly["current_fraud_count"] = (
    weekly["fraud_count"]
)


# Previous behaviour
weekly["previous_transaction_count"] = (
    weekly["transaction_count"]
    .shift(1)
)


weekly["previous_avg_transaction_amount"] = (
    weekly["avg_transaction_amount"]
    .shift(1)
)


# --------------------------------------------------
# 8. Trend Features
# --------------------------------------------------

weekly["spending_change"] = (

    weekly["current_week_spending"]

    -

    weekly["spending_1_week_ago"]
)


weekly["spending_change_percentage"] = (

    weekly["spending_change"]

    /

    weekly["spending_1_week_ago"]
    .replace(0, np.nan)

) * 100


# --------------------------------------------------
# 9. Prediction Target
# --------------------------------------------------

weekly["next_week_spending"] = (

    weekly["weekly_spending"]
    .shift(-1)
)


# --------------------------------------------------
# 10. Remove Missing Lag / Target Rows
# --------------------------------------------------

weekly = weekly.dropna().reset_index(
    drop=True
)


# --------------------------------------------------
# 11. Save Dataset
# --------------------------------------------------

output_path = (
    "data/budget_prediction_dataset.csv"
)


weekly.to_csv(
    output_path,
    index=False
)


# --------------------------------------------------
# 12. Display Results
# --------------------------------------------------

print(
    "\nBudget Prediction Dataset "
    "Created Successfully!"
)


print(
    "\nFinal Dataset Shape:",
    weekly.shape
)


print("\nColumns:")

for column in weekly.columns:
    print("-", column)


print("\nCorrelation With Next Week Spending:")

correlation_columns = [

    "current_week_spending",
    "spending_1_week_ago",
    "spending_2_weeks_ago",
    "previous_2_week_avg",
    "previous_4_week_avg",
    "previous_8_week_avg",
    "current_transaction_count",
    "current_avg_transaction_amount",
    "next_week_spending"
]


print(
    weekly[
        correlation_columns
    ]
    .corr()[
        "next_week_spending"
    ]
    .sort_values(
        ascending=False
    )
)


print(
    "\nSample Data:"
)

print(
    weekly.head()
)


print(
    "\nDataset Saved To:",
    output_path
)