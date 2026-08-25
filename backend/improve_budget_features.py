import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. SETTINGS
# ============================================================

DATA_PATH = "data/budget_prediction_dataset.csv"
TARGET = "next_week_spending"

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)


# ============================================================
# 2. LOAD DATASET
# ============================================================

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

print("=" * 80)
print("ADVANCED BUDGET FEATURE ENGINEERING")
print("=" * 80)

print("\nDataset Loaded")
print("Shape:", data.shape)


# ============================================================
# 3. SAFE DIVISION HELPER
# ============================================================

def safe_divide(a, b):
    return np.where(
        np.abs(b) > 1e-9,
        a / b,
        0.0
    )


# ============================================================
# 4. FEATURE ENGINEERING
# ============================================================

# ------------------------------------------------------------
# Lag momentum
# ------------------------------------------------------------

data["lag_1_change"] = (
    data["current_week_spending"]
    - data["spending_1_week_ago"]
)

data["lag_2_change"] = (
    data["spending_1_week_ago"]
    - data["spending_2_weeks_ago"]
)

data["lag_3_change"] = (
    data["spending_2_weeks_ago"]
    - data["spending_3_weeks_ago"]
)

data["lag_4_change"] = (
    data["spending_3_weeks_ago"]
    - data["spending_4_weeks_ago"]
)


# ------------------------------------------------------------
# Percentage momentum
# ------------------------------------------------------------

data["current_vs_last_week_pct"] = (
    safe_divide(
        data["current_week_spending"]
        - data["spending_1_week_ago"],

        data["spending_1_week_ago"]
    )
)

data["last_week_vs_2week_pct"] = (
    safe_divide(
        data["spending_1_week_ago"]
        - data["spending_2_weeks_ago"],

        data["spending_2_weeks_ago"]
    )
)


# ------------------------------------------------------------
# Historical mean relationships
# ------------------------------------------------------------

data["current_vs_2week_avg_ratio"] = (
    safe_divide(
        data["current_week_spending"],
        data["previous_2_week_avg"]
    )
)

data["current_vs_4week_avg_ratio"] = (
    safe_divide(
        data["current_week_spending"],
        data["previous_4_week_avg"]
    )
)

data["current_vs_8week_avg_ratio"] = (
    safe_divide(
        data["current_week_spending"],
        data["previous_8_week_avg"]
    )
)


# ------------------------------------------------------------
# Distance from historical averages
# ------------------------------------------------------------

data["current_minus_2week_avg"] = (
    data["current_week_spending"]
    - data["previous_2_week_avg"]
)

data["current_minus_4week_avg"] = (
    data["current_week_spending"]
    - data["previous_4_week_avg"]
)

data["current_minus_8week_avg"] = (
    data["current_week_spending"]
    - data["previous_8_week_avg"]
)


# ------------------------------------------------------------
# Four-week spending statistics
# ------------------------------------------------------------

lag_columns = [
    "spending_1_week_ago",
    "spending_2_weeks_ago",
    "spending_3_weeks_ago",
    "spending_4_weeks_ago"
]

data["lag_4week_mean"] = (
    data[lag_columns].mean(axis=1)
)

data["lag_4week_std"] = (
    data[lag_columns].std(
        axis=1,
        ddof=0
    )
)

data["lag_4week_min"] = (
    data[lag_columns].min(axis=1)
)

data["lag_4week_max"] = (
    data[lag_columns].max(axis=1)
)

data["lag_4week_range"] = (
    data["lag_4week_max"]
    - data["lag_4week_min"]
)


# ------------------------------------------------------------
# Coefficient of variation
# ------------------------------------------------------------

data["lag_4week_cv"] = (
    safe_divide(
        data["lag_4week_std"],
        data["lag_4week_mean"]
    )
)


# ------------------------------------------------------------
# Simple trend
# ------------------------------------------------------------

data["recent_trend"] = (
    (
        data["current_week_spending"]
        - data["spending_4_weeks_ago"]
    ) / 4.0
)

data["short_term_trend"] = (
    data["current_week_spending"]
    - data["previous_2_week_avg"]
)


# ------------------------------------------------------------
# Transaction behaviour
# ------------------------------------------------------------

data["transaction_count_change"] = (
    data["current_transaction_count"]
    - data["previous_transaction_count"]
)

data["avg_transaction_change"] = (
    data["current_avg_transaction_amount"]
    - data["previous_avg_transaction_amount"]
)

data["avg_transaction_ratio"] = (
    safe_divide(
        data["current_avg_transaction_amount"],
        data["previous_avg_transaction_amount"]
    )
)


# ------------------------------------------------------------
# Fraud ratios
# ------------------------------------------------------------

data["fraud_rate"] = (
    safe_divide(
        data["current_fraud_count"],
        data["current_transaction_count"]
    )
)


# ------------------------------------------------------------
# Calendar features
# ------------------------------------------------------------

data["month"] = (
    data["week_end"].dt.month
)

data["quarter"] = (
    data["week_end"].dt.quarter
)

data["year"] = (
    data["week_end"].dt.year
)

data["month_sin"] = np.sin(
    2 * np.pi
    * data["month"]
    / 12
)

data["month_cos"] = np.cos(
    2 * np.pi
    * data["month"]
    / 12
)

data["quarter_sin"] = np.sin(
    2 * np.pi
    * data["quarter"]
    / 4
)

data["quarter_cos"] = np.cos(
    2 * np.pi
    * data["quarter"]
    / 4
)


# ============================================================
# 5. FEATURE SETS
# ============================================================

current_features = [

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


engineered_features = [

    # Current production features
    *current_features,

    # Momentum
    "lag_1_change",
    "lag_2_change",
    "lag_3_change",
    "lag_4_change",

    "current_vs_last_week_pct",
    "last_week_vs_2week_pct",

    # Historical relationships
    "current_vs_2week_avg_ratio",
    "current_vs_4week_avg_ratio",
    "current_vs_8week_avg_ratio",

    "current_minus_2week_avg",
    "current_minus_4week_avg",
    "current_minus_8week_avg",

    # Volatility
    "lag_4week_mean",
    "lag_4week_std",
    "lag_4week_min",
    "lag_4week_max",
    "lag_4week_range",
    "lag_4week_cv",

    # Trend
    "recent_trend",
    "short_term_trend",

    # Behaviour
    "transaction_count_change",
    "avg_transaction_change",
    "avg_transaction_ratio",

    "fraud_rate",

    # Calendar
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "quarter_sin",
    "quarter_cos"
]


compact_engineered_features = [

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

    "spending_change",
    "spending_change_percentage",

    "week_sin",
    "week_cos",

    "current_vs_last_week_pct",

    "current_vs_4week_avg_ratio",

    "lag_4week_std",
    "lag_4week_range",

    "recent_trend",
    "short_term_trend",

    "transaction_count_change",
    "avg_transaction_ratio",

    "fraud_rate",

    "month_sin",
    "month_cos"
]


feature_sets = {

    "Current Features":
        current_features,

    "Compact Engineered":
        compact_engineered_features,

    "Full Engineered":
        engineered_features
}


# ============================================================
# 6. CLEAN DATA
# ============================================================

all_required = list(
    set(
        engineered_features
        + [TARGET]
    )
)

data = data.replace(
    [np.inf, -np.inf],
    np.nan
)

data = data.dropna(
    subset=all_required
).reset_index(drop=True)

print(
    "\nSamples After Feature Engineering:",
    len(data)
)


# ============================================================
# 7. CHRONOLOGICAL HOLDOUT SPLIT
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

y_train = train_data[
    TARGET
]

y_test = test_data[
    TARGET
]

print(
    "Training Samples:",
    len(train_data)
)

print(
    "Testing Samples :",
    len(test_data)
)


# ============================================================
# 8. MODELS
# ============================================================

models = {

    "Linear Regression":
        LinearRegression(),

    "Ridge Regression":
        Ridge(
            alpha=10.0
        ),

    "Gradient Boosting Current":
        GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=2,
            random_state=42
        ),

    "Gradient Boosting Conservative":
        GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.02,
            max_depth=1,
            min_samples_leaf=3,
            subsample=0.8,
            random_state=42
        ),

    "Gradient Boosting Medium":
        GradientBoostingRegressor(
            n_estimators=250,
            learning_rate=0.025,
            max_depth=2,
            min_samples_leaf=2,
            subsample=0.9,
            random_state=42
        ),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=500,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),

    "Extra Trees":
        ExtraTreesRegressor(
            n_estimators=500,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),

    "Hist Gradient Boosting":
        HistGradientBoostingRegressor(
            learning_rate=0.04,
            max_iter=300,
            max_leaf_nodes=10,
            l2_regularization=1.0,
            random_state=42
        )
}


# ============================================================
# 9. TIME SERIES CROSS VALIDATION
# ============================================================

tscv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 10. TRAIN AND EVALUATE
# ============================================================

results = []

best_model_object = None
best_features = None
best_model_name = None
best_feature_set_name = None

best_test_r2 = -np.inf


for feature_set_name, features in feature_sets.items():

    print("\n" + "=" * 80)
    print("FEATURE SET:", feature_set_name)
    print("=" * 80)

    X_train = train_data[
        features
    ]

    X_test = test_data[
        features
    ]


    for model_name, model in models.items():

        cv_scores = cross_val_score(

            model,

            X_train,

            y_train,

            cv=tscv,

            scoring="r2",

            n_jobs=-1
        )

        cv_mean = (
            cv_scores.mean()
        )

        cv_std = (
            cv_scores.std()
        )


        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )


        r2 = r2_score(
            y_test,
            predictions
        )

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                predictions
            )
        )


        results.append({

            "Feature Set":
                feature_set_name,

            "Model":
                model_name,

            "Feature Count":
                len(features),

            "CV R2 Mean":
                cv_mean,

            "CV R2 Std":
                cv_std,

            "Test R2":
                r2,

            "MAE":
                mae,

            "RMSE":
                rmse
        })


        print(
            f"{model_name:32s}"
            f" CV={cv_mean:8.4f}"
            f" | Test R2={r2:8.4f}"
            f" | RMSE={rmse:9.2f}"
            f" | MAE={mae:9.2f}"
        )


        if r2 > best_test_r2:

            best_test_r2 = r2

            best_model_object = model

            best_features = features

            best_model_name = (
                model_name
            )

            best_feature_set_name = (
                feature_set_name
            )


# ============================================================
# 11. RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(

    by=[
        "Test R2",
        "CV R2 Mean"
    ],

    ascending=False

).reset_index(drop=True)


print("\n" + "=" * 100)
print("FINAL FEATURE ENGINEERING MODEL RANKING")
print("=" * 100)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 12. NAIVE BASELINE
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


print("\n" + "=" * 80)
print("NAIVE BASELINE")
print("=" * 80)

print(
    "R2   :",
    round(
        naive_r2,
        4
    )
)

print(
    "RMSE :",
    round(
        naive_rmse,
        2
    )
)

print(
    "MAE  :",
    round(
        naive_mae,
        2
    )
)


# ============================================================
# 13. CURRENT PRODUCTION REFERENCE
# ============================================================

CURRENT_PRODUCTION_R2 = 0.599702

print("\n" + "=" * 80)
print("BEST CANDIDATE")
print("=" * 80)

best_row = results_df.iloc[0]

print(
    "Feature Set :",
    best_row["Feature Set"]
)

print(
    "Model       :",
    best_row["Model"]
)

print(
    "Feature Count:",
    int(
        best_row["Feature Count"]
    )
)

print(
    "CV R2 Mean  :",
    round(
        best_row["CV R2 Mean"],
        4
    )
)

print(
    "CV R2 Std   :",
    round(
        best_row["CV R2 Std"],
        4
    )
)

print(
    "Test R2     :",
    round(
        best_row["Test R2"],
        4
    )
)

print(
    "Test RMSE   :",
    round(
        best_row["RMSE"],
        2
    )
)

print(
    "Test MAE    :",
    round(
        best_row["MAE"],
        2
    )
)


# ============================================================
# 14. PRODUCTION REPLACEMENT DECISION
# ============================================================

new_r2 = float(
    best_row["Test R2"]
)

new_cv = float(
    best_row["CV R2 Mean"]
)

improvement = (
    new_r2
    - CURRENT_PRODUCTION_R2
)


print("\n" + "=" * 80)
print("PRODUCTION DECISION")
print("=" * 80)

print(
    "Current Production Test R2:",
    CURRENT_PRODUCTION_R2
)

print(
    "New Candidate Test R2     :",
    round(
        new_r2,
        6
    )
)

print(
    "R2 Improvement            :",
    round(
        improvement,
        6
    )
)


if (
    new_r2 > CURRENT_PRODUCTION_R2
    and new_cv > 0
):

    recommendation = (
        "CANDIDATE_FOR_PRODUCTION"
    )

    print(
        "\nRecommendation:"
    )

    print(
        "Candidate improves holdout R2 "
        "and has positive TimeSeries CV."
    )

else:

    recommendation = (
        "KEEP_CURRENT_PRODUCTION_MODEL"
    )

    print(
        "\nRecommendation:"
    )

    print(
        "Keep current production model."
    )


# ============================================================
# 15. SAVE RESULTS
# ============================================================

results_df.to_csv(
    "data/improved_budget_feature_results.csv",
    index=False
)


joblib.dump(
    best_model_object,
    "models/budget_feature_engineering_candidate.pkl"
)

joblib.dump(
    best_features,
    "models/budget_feature_engineering_candidate_features.pkl"
)


metadata = {

    "candidate_model":
        best_model_name,

    "feature_set":
        best_feature_set_name,

    "feature_count":
        len(best_features),

    "features":
        best_features,

    "metrics": {

        "cv_r2_mean":
            float(
                best_row["CV R2 Mean"]
            ),

        "cv_r2_std":
            float(
                best_row["CV R2 Std"]
            ),

        "test_r2":
            float(
                best_row["Test R2"]
            ),

        "test_rmse":
            float(
                best_row["RMSE"]
            ),

        "test_mae":
            float(
                best_row["MAE"]
            )
    },

    "current_production_r2":
        CURRENT_PRODUCTION_R2,

    "test_r2_improvement":
        improvement,

    "recommendation":
        recommendation
}


with open(
    "data/improved_budget_feature_metadata.json",
    "w"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


# ============================================================
# 16. SAVE ENGINEERED DATASET
# ============================================================

data.to_csv(
    "data/budget_prediction_dataset_engineered.csv",
    index=False
)


print("\n" + "=" * 80)
print("FILES SAVED")
print("=" * 80)

print(
    "data/improved_budget_feature_results.csv"
)

print(
    "data/improved_budget_feature_metadata.json"
)

print(
    "data/budget_prediction_dataset_engineered.csv"
)

print(
    "models/budget_feature_engineering_candidate.pkl"
)

print(
    "models/budget_feature_engineering_candidate_features.pkl"
)


print(
    "\nFeature engineering evaluation completed."
)