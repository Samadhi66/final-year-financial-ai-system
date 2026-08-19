import pandas as pd
import numpy as np
import os
import joblib

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
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

print("Budget Prediction Dataset Loaded")
print("Dataset Shape:", data.shape)


# ============================================================
# 2. FEATURES AND TARGET
# ============================================================

features = [

    "week_sin",
    "week_cos",

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
    "current_fraud_count",

    "previous_transaction_count",
    "previous_avg_transaction_amount",

    "spending_change",
    "spending_change_percentage"
]

target = "next_week_spending"

X = data[features]
y = data[target]

print("\nFeatures Used:")
for feature in features:
    print("-", feature)

print("\nTarget:", target)


# ============================================================
# 3. CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\n====================================")
print("CHRONOLOGICAL SPLIT")
print("====================================")

print("Training Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# ============================================================
# 4. BASE GRADIENT BOOSTING MODEL
# ============================================================

base_model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=2,
    random_state=42
)

base_model.fit(
    X_train,
    y_train
)

base_predictions = base_model.predict(
    X_test
)

base_mae = mean_absolute_error(
    y_test,
    base_predictions
)

base_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        base_predictions
    )
)

base_r2 = r2_score(
    y_test,
    base_predictions
)

print("\n====================================")
print("BASE GRADIENT BOOSTING PERFORMANCE")
print("====================================")

print("MAE :", round(base_mae, 2))
print("RMSE:", round(base_rmse, 2))
print("R2  :", round(base_r2, 4))


# ============================================================
# 5. TIME SERIES CROSS VALIDATION
# ============================================================

tscv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 6. HYPERPARAMETER SEARCH SPACE
# ============================================================

param_distributions = {

    "n_estimators": [
        100,
        200,
        300,
        400,
        500
    ],

    "learning_rate": [
        0.01,
        0.03,
        0.05,
        0.08,
        0.10
    ],

    "max_depth": [
        1,
        2,
        3,
        4
    ],

    "min_samples_split": [
        2,
        4,
        6,
        10
    ],

    "min_samples_leaf": [
        1,
        2,
        3,
        4,
        6
    ],

    "subsample": [
        0.7,
        0.8,
        0.9,
        1.0
    ],

    "max_features": [
        None,
        "sqrt",
        "log2"
    ]
}


# ============================================================
# 7. RANDOMIZED SEARCH
# ============================================================

model = GradientBoostingRegressor(
    random_state=42
)

search = RandomizedSearchCV(

    estimator=model,

    param_distributions=param_distributions,

    n_iter=80,

    scoring="r2",

    cv=tscv,

    random_state=42,

    n_jobs=-1,

    verbose=1
)

print("\n====================================")
print("STARTING GRADIENT BOOSTING TUNING")
print("====================================")

search.fit(
    X_train,
    y_train
)


# ============================================================
# 8. BEST HYPERPARAMETERS
# ============================================================

print("\n====================================")
print("BEST HYPERPARAMETERS")
print("====================================")

print(
    search.best_params_
)

print(
    "\nBest Time-Series CV R2:",
    round(
        search.best_score_,
        4
    )
)


# ============================================================
# 9. TUNED MODEL EVALUATION
# ============================================================

best_model = search.best_estimator_

predictions = best_model.predict(
    X_test
)

tuned_mae = mean_absolute_error(
    y_test,
    predictions
)

tuned_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

tuned_r2 = r2_score(
    y_test,
    predictions
)

print("\n====================================")
print("TUNED GRADIENT BOOSTING PERFORMANCE")
print("====================================")

print(
    "MAE :",
    round(
        tuned_mae,
        2
    )
)

print(
    "RMSE:",
    round(
        tuned_rmse,
        2
    )
)

print(
    "R2  :",
    round(
        tuned_r2,
        4
    )
)


# ============================================================
# 10. NAIVE FORECAST BASELINE
# ============================================================

naive_predictions = (
    X_test[
        "current_week_spending"
    ].values
)

naive_mae = mean_absolute_error(
    y_test,
    naive_predictions
)

naive_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        naive_predictions
    )
)

naive_r2 = r2_score(
    y_test,
    naive_predictions
)

print("\n====================================")
print("NAIVE FORECAST BASELINE")
print("====================================")

print(
    "MAE :",
    round(
        naive_mae,
        2
    )
)

print(
    "RMSE:",
    round(
        naive_rmse,
        2
    )
)

print(
    "R2  :",
    round(
        naive_r2,
        4
    )
)


# ============================================================
# 11. BASE VS TUNED VS NAIVE COMPARISON
# ============================================================

comparison = pd.DataFrame({

    "Model": [
        "Base Gradient Boosting",
        "Tuned Gradient Boosting",
        "Naive Forecast"
    ],

    "MAE": [
        base_mae,
        tuned_mae,
        naive_mae
    ],

    "RMSE": [
        base_rmse,
        tuned_rmse,
        naive_rmse
    ],

    "R2 Score": [
        base_r2,
        tuned_r2,
        naive_r2
    ]
})

comparison = comparison.sort_values(
    by="R2 Score",
    ascending=False
).reset_index(drop=True)

print("\n====================================")
print("FINAL PERFORMANCE COMPARISON")
print("====================================")

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 12. SAVE TUNING RESULTS
# ============================================================

comparison.to_csv(
    "data/gradient_boosting_tuning_results.csv",
    index=False
)


# ============================================================
# 13. SAVE FINAL MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    best_model,
    "models/best_gradient_boosting_budget_model.pkl"
)

print("\n====================================")
print("MODEL SAVED SUCCESSFULLY")
print("====================================")

print(
    "models/best_gradient_boosting_budget_model.pkl"
)