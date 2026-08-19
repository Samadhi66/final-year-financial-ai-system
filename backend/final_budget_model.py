import pandas as pd
import numpy as np
import os
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

data = pd.read_csv(
    "data/budget_prediction_dataset.csv"
)

data["week_end"] = pd.to_datetime(
    data["week_end"]
)

data = data.sort_values(
    "week_end"
).reset_index(drop=True)

print("=" * 65)
print("FINAL BUDGET PREDICTION MODEL")
print("=" * 65)

print("\nDataset Loaded Successfully")
print("Dataset Shape:", data.shape)


# ============================================================
# 2. SELECT FINAL FEATURE SET
# ============================================================

features = [

    # Seasonal information
    "week_sin",
    "week_cos",

    # Current week behaviour
    "current_week_spending",

    # Historical spending
    "spending_1_week_ago",
    "spending_2_weeks_ago",
    "spending_3_weeks_ago",
    "spending_4_weeks_ago",

    # Rolling averages
    "previous_2_week_avg",
    "previous_4_week_avg",
    "previous_8_week_avg",

    # Current transaction behaviour
    "current_transaction_count",
    "current_avg_transaction_amount",
    "current_fraud_count",

    # Previous transaction behaviour
    "previous_transaction_count",
    "previous_avg_transaction_amount",

    # Spending trend
    "spending_change",
    "spending_change_percentage"
]

target = "next_week_spending"


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = features + [target]

missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing_columns:

    print("\nERROR: Missing columns detected:")

    for column in missing_columns:
        print("-", column)

    raise ValueError(
        "Required columns are missing from dataset."
    )


X = data[features]
y = data[target]


print("\nFeatures Used:")

for feature in features:
    print("-", feature)

print("\nTarget:", target)


# ============================================================
# 4. CHRONOLOGICAL 80/20 SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


print("\n" + "=" * 65)
print("CHRONOLOGICAL TRAIN / TEST SPLIT")
print("=" * 65)

print("Training Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# ============================================================
# 5. EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    model_name,
    actual,
    predictions
):

    mae = mean_absolute_error(
        actual,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predictions
        )
    )

    r2 = r2_score(
        actual,
        predictions
    )

    return {
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2 Score": r2
    }


results = []


# ============================================================
# 6. LINEAR REGRESSION BASELINE
# ============================================================

print("\nTraining Linear Regression Baseline...")

linear_model = LinearRegression()

linear_model.fit(
    X_train,
    y_train
)

linear_predictions = linear_model.predict(
    X_test
)

linear_results = evaluate_model(
    "Linear Regression",
    y_test,
    linear_predictions
)

results.append(
    linear_results
)


# ============================================================
# 7. NAIVE FORECAST BASELINE
# ============================================================

print("Evaluating Naive Forecast Baseline...")

naive_predictions = (
    X_test["current_week_spending"]
    .to_numpy()
)

naive_results = evaluate_model(
    "Naive Forecast",
    y_test,
    naive_predictions
)

results.append(
    naive_results
)


# ============================================================
# 8. FINAL GRADIENT BOOSTING MODEL
# ============================================================

print("Training Gradient Boosting Model...")

gradient_boosting_model = GradientBoostingRegressor(

    n_estimators=300,

    learning_rate=0.03,

    max_depth=2,

    random_state=42
)

gradient_boosting_model.fit(
    X_train,
    y_train
)

gb_predictions = gradient_boosting_model.predict(
    X_test
)

gb_results = evaluate_model(
    "Gradient Boosting",
    y_test,
    gb_predictions
)

results.append(
    gb_results
)


# ============================================================
# 9. FINAL COMPARISON
# ============================================================

comparison = pd.DataFrame(
    results
)

comparison = comparison.sort_values(
    by="R2 Score",
    ascending=False
).reset_index(drop=True)


print("\n" + "=" * 65)
print("FINAL MODEL COMPARISON")
print("=" * 65)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 10. GRADIENT BOOSTING FINAL RESULTS
# ============================================================

print("\n" + "=" * 65)
print("SELECTED ADVANCED MODEL")
print("=" * 65)

print("Model: Gradient Boosting")

print(
    "R2 Score:",
    round(
        gb_results["R2 Score"],
        4
    )
)

print(
    "MAE:",
    round(
        gb_results["MAE"],
        2
    )
)

print(
    "RMSE:",
    round(
        gb_results["RMSE"],
        2
    )
)


# ============================================================
# 11. COMPARE AGAINST BASELINES
# ============================================================

print("\n" + "=" * 65)
print("BASELINE COMPARISON")
print("=" * 65)

print(
    "Linear Regression R2:",
    round(
        linear_results["R2 Score"],
        4
    )
)

print(
    "Naive Forecast R2:",
    round(
        naive_results["R2 Score"],
        4
    )
)

print(
    "Gradient Boosting R2:",
    round(
        gb_results["R2 Score"],
        4
    )
)


# ============================================================
# 12. SAVE FINAL RESULTS
# ============================================================

comparison.to_csv(
    "data/final_budget_model_results.csv",
    index=False
)


# ============================================================
# 13. SAVE FINAL GRADIENT BOOSTING MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    gradient_boosting_model,
    "models/final_gradient_boosting_budget_model.pkl"
)


# Save feature list as well

joblib.dump(
    features,
    "models/final_budget_model_features.pkl"
)


print("\n" + "=" * 65)
print("FINAL MODEL SAVED SUCCESSFULLY")
print("=" * 65)

print(
    "Model:",
    "models/final_gradient_boosting_budget_model.pkl"
)

print(
    "Features:",
    "models/final_budget_model_features.pkl"
)

print(
    "Results:",
    "data/final_budget_model_results.csv"
)