import pandas as pd
import numpy as np
import os
import joblib

from sklearn.ensemble import ExtraTreesRegressor
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

print("Budget Prediction Dataset Loaded")
print("Dataset Shape:", data.shape)


# ============================================================
# 2. SORT CHRONOLOGICALLY
# ============================================================

data = data.sort_values(
    ["year", "week"]
).reset_index(drop=True)


# ============================================================
# 3. FEATURES AND TARGET
# ============================================================

features = [
    "week",

    "previous_week_spending",
    "spending_2_weeks_ago",
    "spending_3_weeks_ago",
    "spending_4_weeks_ago",

    "previous_2_week_avg",
    "previous_4_week_avg",

    "previous_transaction_count",
    "previous_avg_transaction_amount",

    "previous_fraud_count",

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
# 4. CHRONOLOGICAL TRAIN-TEST SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


print("\nChronological Split")
print("-------------------")
print("Training Samples:", len(X_train))
print("Testing Samples:", len(X_test))


# ============================================================
# 5. BASE EXTRA TREES MODEL
# ============================================================

base_model = ExtraTreesRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
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
print("BASE EXTRA TREES PERFORMANCE")
print("====================================")

print("MAE :", round(base_mae, 2))
print("RMSE:", round(base_rmse, 2))
print("R2  :", round(base_r2, 4))


# ============================================================
# 6. TIME SERIES CROSS VALIDATION
# ============================================================

time_series_cv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 7. HYPERPARAMETER SEARCH SPACE
# ============================================================

parameter_grid = {

    "n_estimators": [
        200,
        300,
        500,
        700
    ],

    "max_depth": [
        None,
        5,
        10,
        15,
        20,
        30
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

    "max_features": [
        1.0,
        "sqrt",
        "log2"
    ],

    "bootstrap": [
        False,
        True
    ]
}


# ============================================================
# 8. RANDOMIZED SEARCH
# ============================================================

extra_trees = ExtraTreesRegressor(
    random_state=42,
    n_jobs=-1
)


search = RandomizedSearchCV(

    estimator=extra_trees,

    param_distributions=parameter_grid,

    n_iter=60,

    scoring="r2",

    cv=time_series_cv,

    random_state=42,

    n_jobs=-1,

    verbose=1
)


print("\n====================================")
print("STARTING EXTRA TREES TUNING")
print("====================================")


search.fit(
    X_train,
    y_train
)


# ============================================================
# 9. BEST PARAMETERS
# ============================================================

print("\n====================================")
print("BEST HYPERPARAMETERS")
print("====================================")

print(search.best_params_)

print(
    "\nBest Time-Series CV R2:",
    round(search.best_score_, 4)
)


# ============================================================
# 10. FINAL TUNED MODEL
# ============================================================

best_model = search.best_estimator_

predictions = best_model.predict(
    X_test
)


final_mae = mean_absolute_error(
    y_test,
    predictions
)

final_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

final_r2 = r2_score(
    y_test,
    predictions
)


# ============================================================
# 11. FINAL PERFORMANCE
# ============================================================

print("\n====================================")
print("TUNED EXTRA TREES PERFORMANCE")
print("====================================")

print("MAE :", round(final_mae, 2))
print("RMSE:", round(final_rmse, 2))
print("R2  :", round(final_r2, 4))


# ============================================================
# 12. BEFORE / AFTER COMPARISON
# ============================================================

comparison = pd.DataFrame({

    "Model": [
        "Base Extra Trees",
        "Tuned Extra Trees"
    ],

    "MAE": [
        base_mae,
        final_mae
    ],

    "RMSE": [
        base_rmse,
        final_rmse
    ],

    "R2 Score": [
        base_r2,
        final_r2
    ]
})


print("\n====================================")
print("TUNING COMPARISON")
print("====================================")

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 13. SAVE RESULTS
# ============================================================

comparison.to_csv(
    "data/extra_trees_tuning_results.csv",
    index=False
)


# ============================================================
# 14. SAVE FINAL MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)


joblib.dump(
    best_model,
    "models/best_extra_trees_budget_model.pkl"
)


print("\n====================================")
print("MODEL SAVED SUCCESSFULLY")
print("====================================")

print(
    "models/best_extra_trees_budget_model.pkl"
)