import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import (
    TimeSeriesSplit,
    RandomizedSearchCV,
    cross_val_score
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = "data/budget_prediction_dataset.csv"

data = pd.read_csv(DATA_PATH)

data["week_end"] = pd.to_datetime(
    data["week_end"],
    errors="coerce"
)

data = data.dropna(
    subset=["week_end"]
)

data = data.sort_values(
    "week_end"
).reset_index(drop=True)

print("=" * 70)
print("BUDGET MODEL HYPERPARAMETER TUNING")
print("=" * 70)

print("\nDataset Loaded")
print("Shape:", data.shape)


# ============================================================
# 2. TARGET
# ============================================================

target = "next_week_spending"


# ============================================================
# 3. FULL FEATURE SET
# ============================================================

features = [

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
    "spending_change_percentage",

    "week_sin",
    "week_cos"
]


# ============================================================
# 4. CLEAN REQUIRED COLUMNS
# ============================================================

required_columns = (
    features +
    [target]
)

data = data.dropna(
    subset=required_columns
).reset_index(drop=True)

print(
    "Samples after cleaning:",
    len(data)
)


# ============================================================
# 5. CHRONOLOGICAL 80/20 SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

train_data = data.iloc[
    :split_index
].copy()

test_data = data.iloc[
    split_index:
].copy()

X_train = train_data[
    features
]

y_train = train_data[
    target
]

X_test = test_data[
    features
]

y_test = test_data[
    target
]


print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# ============================================================
# 6. TIME SERIES CROSS VALIDATION
# ============================================================

tscv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 7. CURRENT GRADIENT BOOSTING MODEL
# ============================================================

current_model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=2,
    random_state=42
)

current_model.fit(
    X_train,
    y_train
)

current_predictions = (
    current_model.predict(
        X_test
    )
)

current_r2 = r2_score(
    y_test,
    current_predictions
)

current_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        current_predictions
    )
)

current_mae = mean_absolute_error(
    y_test,
    current_predictions
)

current_cv_scores = cross_val_score(
    current_model,
    X_train,
    y_train,
    cv=tscv,
    scoring="r2",
    n_jobs=-1
)

current_cv_mean = (
    current_cv_scores.mean()
)

current_cv_std = (
    current_cv_scores.std()
)


print("\n" + "=" * 70)
print("CURRENT GRADIENT BOOSTING")
print("=" * 70)

print(
    f"CV R2 Mean : "
    f"{current_cv_mean:.4f}"
)

print(
    f"CV R2 Std  : "
    f"{current_cv_std:.4f}"
)

print(
    f"Test R2    : "
    f"{current_r2:.4f}"
)

print(
    f"Test RMSE  : "
    f"{current_rmse:.2f}"
)

print(
    f"Test MAE   : "
    f"{current_mae:.2f}"
)


# ============================================================
# 8. HYPERPARAMETER SEARCH SPACE
# ============================================================

parameter_grid = {

    "n_estimators": [
        100,
        150,
        200,
        250,
        300,
        400,
        500
    ],

    "learning_rate": [
        0.01,
        0.02,
        0.03,
        0.05,
        0.07,
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
        8,
        10
    ],

    "min_samples_leaf": [
        1,
        2,
        3,
        4,
        5
    ],

    "subsample": [
        0.6,
        0.7,
        0.8,
        0.9,
        1.0
    ],

    "max_features": [
        None,
        "sqrt",
        "log2"
    ],

    "loss": [
        "squared_error",
        "huber"
    ]
}


# ============================================================
# 9. RANDOMIZED SEARCH
# ============================================================

base_model = GradientBoostingRegressor(
    random_state=42
)

random_search = RandomizedSearchCV(

    estimator=base_model,

    param_distributions=
        parameter_grid,

    n_iter=80,

    scoring=
        "neg_mean_squared_error",

    cv=tscv,

    random_state=42,

    n_jobs=-1,

    verbose=1,

    refit=True
)


print("\n" + "=" * 70)
print("STARTING HYPERPARAMETER SEARCH")
print("=" * 70)

random_search.fit(
    X_train,
    y_train
)


# ============================================================
# 10. BEST PARAMETERS
# ============================================================

best_model = (
    random_search.best_estimator_
)

print("\n" + "=" * 70)
print("BEST PARAMETERS")
print("=" * 70)

for key, value in (
    random_search
    .best_params_
    .items()
):
    print(
        f"{key:22s}: {value}"
    )


# ============================================================
# 11. TUNED MODEL HOLDOUT EVALUATION
# ============================================================

tuned_predictions = (
    best_model.predict(
        X_test
    )
)

tuned_r2 = r2_score(
    y_test,
    tuned_predictions
)

tuned_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        tuned_predictions
    )
)

tuned_mae = mean_absolute_error(
    y_test,
    tuned_predictions
)


# ============================================================
# 12. TUNED TIME SERIES CV R2
# ============================================================

tuned_cv_scores = cross_val_score(

    best_model,

    X_train,

    y_train,

    cv=tscv,

    scoring="r2",

    n_jobs=-1
)

tuned_cv_mean = (
    tuned_cv_scores.mean()
)

tuned_cv_std = (
    tuned_cv_scores.std()
)


print("\n" + "=" * 70)
print("TUNED GRADIENT BOOSTING RESULTS")
print("=" * 70)

print(
    f"CV R2 Scores : "
    f"{np.round(tuned_cv_scores, 4)}"
)

print(
    f"CV R2 Mean   : "
    f"{tuned_cv_mean:.4f}"
)

print(
    f"CV R2 Std    : "
    f"{tuned_cv_std:.4f}"
)

print(
    f"Test R2      : "
    f"{tuned_r2:.4f}"
)

print(
    f"Test RMSE    : "
    f"{tuned_rmse:.2f}"
)

print(
    f"Test MAE     : "
    f"{tuned_mae:.2f}"
)


# ============================================================
# 13. LINEAR REGRESSION BASELINE
# ============================================================

linear_model = LinearRegression()

linear_model.fit(
    X_train,
    y_train
)

linear_predictions = (
    linear_model.predict(
        X_test
    )
)

linear_r2 = r2_score(
    y_test,
    linear_predictions
)

linear_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        linear_predictions
    )
)

linear_mae = mean_absolute_error(
    y_test,
    linear_predictions
)

linear_cv_scores = cross_val_score(

    linear_model,

    X_train,

    y_train,

    cv=tscv,

    scoring="r2",

    n_jobs=-1
)

linear_cv_mean = (
    linear_cv_scores.mean()
)


# ============================================================
# 14. NAIVE BASELINE
# ============================================================

naive_predictions = (
    test_data[
        "current_week_spending"
    ].values
)

naive_r2 = r2_score(
    y_test,
    naive_predictions
)

naive_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        naive_predictions
    )
)

naive_mae = mean_absolute_error(
    y_test,
    naive_predictions
)


# ============================================================
# 15. FINAL COMPARISON TABLE
# ============================================================

comparison = pd.DataFrame([

    {
        "Model":
            "Current Gradient Boosting",

        "CV R2 Mean":
            current_cv_mean,

        "Test R2":
            current_r2,

        "MAE":
            current_mae,

        "RMSE":
            current_rmse
    },

    {
        "Model":
            "Tuned Gradient Boosting",

        "CV R2 Mean":
            tuned_cv_mean,

        "Test R2":
            tuned_r2,

        "MAE":
            tuned_mae,

        "RMSE":
            tuned_rmse
    },

    {
        "Model":
            "Linear Regression",

        "CV R2 Mean":
            linear_cv_mean,

        "Test R2":
            linear_r2,

        "MAE":
            linear_mae,

        "RMSE":
            linear_rmse
    },

    {
        "Model":
            "Naive Forecast",

        "CV R2 Mean":
            np.nan,

        "Test R2":
            naive_r2,

        "MAE":
            naive_mae,

        "RMSE":
            naive_rmse
    }

])


comparison = comparison.sort_values(

    by=[
        "Test R2",
        "RMSE"
    ],

    ascending=[
        False,
        True
    ]

).reset_index(drop=True)


print("\n" + "=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 16. IMPROVEMENT SUMMARY
# ============================================================

r2_improvement = (
    tuned_r2 -
    current_r2
)

rmse_improvement = (
    current_rmse -
    tuned_rmse
)

mae_improvement = (
    current_mae -
    tuned_mae
)


print("\n" + "=" * 70)
print("TUNING IMPROVEMENT")
print("=" * 70)

print(
    f"R2 Change   : "
    f"{r2_improvement:+.4f}"
)

print(
    f"RMSE Change : "
    f"{rmse_improvement:+.2f}"
)

print(
    f"MAE Change  : "
    f"{mae_improvement:+.2f}"
)


# ============================================================
# 17. SAVE RESULTS
# ============================================================

os.makedirs(
    "data",
    exist_ok=True
)

os.makedirs(
    "models",
    exist_ok=True
)

comparison.to_csv(
    "data/tuned_budget_model_comparison.csv",
    index=False
)


# Save tuned model separately.
# DO NOT overwrite current production model yet.
joblib.dump(
    best_model,
    "models/budget_gradient_boosting_tuned.pkl"
)

joblib.dump(
    features,
    "models/budget_gradient_boosting_tuned_features.pkl"
)


# ============================================================
# 18. SAVE METADATA
# ============================================================

metadata = {

    "model":
        "Gradient Boosting",

    "best_parameters":
        random_search.best_params_,

    "features":
        features,

    "training_samples":
        int(len(X_train)),

    "testing_samples":
        int(len(X_test)),

    "metrics": {

        "cv_r2_mean":
            float(tuned_cv_mean),

        "cv_r2_std":
            float(tuned_cv_std),

        "test_r2":
            float(tuned_r2),

        "test_rmse":
            float(tuned_rmse),

        "test_mae":
            float(tuned_mae)
    }
}


with open(
    "data/tuned_budget_model_metadata.json",
    "w"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    "data/"
    "tuned_budget_model_comparison.csv"
)

print(
    "data/"
    "tuned_budget_model_metadata.json"
)

print(
    "models/"
    "budget_gradient_boosting_tuned.pkl"
)

print(
    "models/"
    "budget_gradient_boosting_tuned_features.pkl"
)


print("\nTuning completed successfully.")