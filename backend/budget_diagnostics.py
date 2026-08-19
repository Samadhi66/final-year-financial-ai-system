import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

data = pd.read_csv(
    "data/budget_prediction_dataset.csv"
)

data["week_end"] = pd.to_datetime(
    data["week_end"]
)

data = data.sort_values(
    "week_end"
).reset_index(drop=True)


print("=" * 60)
print("BUDGET PREDICTION DATASET DIAGNOSTICS")
print("=" * 60)

print("\nDataset Shape:", data.shape)

print(
    "Start Date:",
    data["week_end"].min()
)

print(
    "End Date:",
    data["week_end"].max()
)


# --------------------------------------------------
# 2. Train / Test Split Information
# --------------------------------------------------

split_index = int(
    len(data) * 0.80
)

train = data.iloc[:split_index]
test = data.iloc[split_index:]


print("\n" + "=" * 60)
print("TRAIN / TEST PERIOD")
print("=" * 60)

print(
    "\nTraining Samples:",
    len(train)
)

print(
    "Testing Samples:",
    len(test)
)

print(
    "\nTraining Period:",
    train["week_end"].min(),
    "to",
    train["week_end"].max()
)

print(
    "Testing Period:",
    test["week_end"].min(),
    "to",
    test["week_end"].max()
)


# --------------------------------------------------
# 3. Target Statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("TARGET STATISTICS")
print("=" * 60)


print("\nTraining Target:")

print(
    train["next_week_spending"].describe()
)


print("\nTesting Target:")

print(
    test["next_week_spending"].describe()
)


# --------------------------------------------------
# 4. Important Correlations
# --------------------------------------------------

important_features = [

    "current_week_spending",

    "spending_1_week_ago",
    "spending_2_weeks_ago",
    "spending_3_weeks_ago",
    "spending_4_weeks_ago",

    "previous_2_week_avg",
    "previous_4_week_avg",
    "previous_8_week_avg",

    "current_transaction_count",
    "current_avg_transaction_amount",

    "previous_transaction_count",
    "previous_avg_transaction_amount",

    "spending_change",
    "spending_change_percentage",

    "next_week_spending"
]


print("\n" + "=" * 60)
print("FULL DATA CORRELATION WITH TARGET")
print("=" * 60)


full_corr = (
    data[important_features]
    .corr()["next_week_spending"]
    .sort_values(
        ascending=False
    )
)

print(full_corr)


# --------------------------------------------------
# 5. Training Correlations
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING CORRELATION WITH TARGET")
print("=" * 60)


train_corr = (
    train[important_features]
    .corr()["next_week_spending"]
    .sort_values(
        ascending=False
    )
)

print(train_corr)


# --------------------------------------------------
# 6. Testing Correlations
# --------------------------------------------------

print("\n" + "=" * 60)
print("TESTING CORRELATION WITH TARGET")
print("=" * 60)


test_corr = (
    test[important_features]
    .corr()["next_week_spending"]
    .sort_values(
        ascending=False
    )
)

print(test_corr)


# --------------------------------------------------
# 7. Persistence / Week-to-Week Relationship
# --------------------------------------------------

actual = data[
    "next_week_spending"
]

current = data[
    "current_week_spending"
]


persistence_corr = (
    current.corr(actual)
)


print("\n" + "=" * 60)
print("WEEK-TO-WEEK PERSISTENCE")
print("=" * 60)

print(
    "\nCurrent Week vs Next Week Correlation:",
    round(
        persistence_corr,
        4
    )
)


# --------------------------------------------------
# 8. Spending Volatility
# --------------------------------------------------

weekly_change = (
    data["next_week_spending"]
    -
    data["current_week_spending"]
)


absolute_change = (
    weekly_change.abs()
)


percentage_change = (

    absolute_change

    /

    data["current_week_spending"]
    .replace(0, np.nan)

) * 100


print("\n" + "=" * 60)
print("WEEKLY SPENDING VOLATILITY")
print("=" * 60)


print(
    "\nAverage Absolute Weekly Change:",
    round(
        absolute_change.mean(),
        2
    )
)


print(
    "Median Absolute Weekly Change:",
    round(
        absolute_change.median(),
        2
    )
)


print(
    "Average Percentage Change:",
    round(
        percentage_change.mean(),
        2
    ),
    "%"
)


# --------------------------------------------------
# 9. Train vs Test Distribution Shift
# --------------------------------------------------

train_mean = (
    train["next_week_spending"].mean()
)

test_mean = (
    test["next_week_spending"].mean()
)


distribution_change = (

    (
        test_mean
        -
        train_mean
    )

    /

    train_mean

) * 100


print("\n" + "=" * 60)
print("TRAIN / TEST DISTRIBUTION SHIFT")
print("=" * 60)


print(
    "\nTraining Mean Spending:",
    round(
        train_mean,
        2
    )
)


print(
    "Testing Mean Spending:",
    round(
        test_mean,
        2
    )
)


print(
    "Mean Difference:",
    round(
        distribution_change,
        2
    ),
    "%"
)


# --------------------------------------------------
# 10. Final Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)


if persistence_corr >= 0.8:

    print(
        "\nStrong week-to-week predictive "
        "relationship detected."
    )

elif persistence_corr >= 0.5:

    print(
        "\nModerate week-to-week predictive "
        "relationship detected."
    )

else:

    print(
        "\nWeak week-to-week predictive "
        "relationship detected."
    )


if abs(distribution_change) > 20:

    print(
        "WARNING: Significant train/test "
        "distribution shift detected."
    )

else:

    print(
        "Train/test spending distributions "
        "are reasonably similar."
    )


print("\nDiagnostics Completed Successfully!")