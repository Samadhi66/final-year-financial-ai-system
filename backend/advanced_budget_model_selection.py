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

print("Dataset Loaded")
print("Shape:", data.shape)


# ============================================================
# 2. TARGET
# ============================================================

target = "next_week_spending"
y = data[target]


# ============================================================
# 3. FEATURE SETS
# ============================================================

feature_sets = {

    "Core Features": [
        "current_week_spending",
        "spending_1_week_ago",
        "previous_2_week_avg",
        "previous_4_week_avg",
        "week_sin",
        "week_cos"
    ],

    "Historical Features": [
        "current_week_spending",
        "spending_1_week_ago",
        "spending_2_weeks_ago",
        "spending_3_weeks_ago",
        "spending_4_weeks_ago",
        "previous_2_week_avg",
        "previous_4_week_avg",
        "previous_8_week_avg",
        "week_sin",
        "week_cos"
    ],

    "Full Features": [
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
}


# ============================================================
# 4. MODELS
# ============================================================

models = {

    "Linear Regression": LinearRegression(),

    "Ridge Regression": Ridge(
        alpha=1.0
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=2,
        random_state=42
    ),

    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=15,
        random_state=42
    )
}


# ============================================================
# 5. CHRONOLOGICAL HOLDOUT SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

train_data = data.iloc[:split_index]
test_data = data.iloc[split_index:]

y_train = train_data[target]
y_test = test_data[target]

print("\nTraining Samples:", len(train_data))
print("Testing Samples :", len(test_data))


# ============================================================
# 6. TIME SERIES CV
# ============================================================

tscv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 7. MODEL + FEATURE SET COMPARISON
# ============================================================

results = []

for feature_set_name, features in feature_sets.items():

    print("\n" + "=" * 60)
    print("FEATURE SET:", feature_set_name)
    print("=" * 60)

    X_train = train_data[features]
    X_test = test_data[features]

    for model_name, model in models.items():

        # -----------------------------
        # Time-Series CV Score
        # -----------------------------

        cv_scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv=tscv,
            scoring="r2",
            n_jobs=-1
        )

        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()


        # -----------------------------
        # Final Holdout Training
        # -----------------------------

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )


        # -----------------------------
        # Evaluation
        # -----------------------------

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

        r2 = r2_score(
            y_test,
            predictions
        )


        results.append({

            "Feature Set":
                feature_set_name,

            "Model":
                model_name,

            "CV R2 Mean":
                cv_mean,

            "CV R2 Std":
                cv_std,

            "Test MAE":
                mae,

            "Test RMSE":
                rmse,

            "Test R2":
                r2
        })


        print(
            f"{model_name:24s}"
            f" CV R2={cv_mean:.4f}"
            f" | Test R2={r2:.4f}"
            f" | RMSE={rmse:.2f}"
        )


# ============================================================
# 8. RESULTS TABLE
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


print("\n" + "=" * 80)
print("FINAL ADVANCED MODEL RANKING")
print("=" * 80)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 9. BEST ADVANCED MODEL ONLY
# ============================================================

advanced_only = results_df[
    ~results_df["Model"].isin(
        [
            "Linear Regression",
            "Ridge Regression"
        ]
    )
].reset_index(drop=True)


best_advanced = advanced_only.iloc[0]


print("\n" + "=" * 80)
print("BEST ADVANCED MODEL")
print("=" * 80)

print(
    "Feature Set :",
    best_advanced["Feature Set"]
)

print(
    "Model       :",
    best_advanced["Model"]
)

print(
    "CV R2 Mean  :",
    round(
        best_advanced["CV R2 Mean"],
        4
    )
)

print(
    "Test R2     :",
    round(
        best_advanced["Test R2"],
        4
    )
)

print(
    "Test RMSE   :",
    round(
        best_advanced["Test RMSE"],
        2
    )
)

print(
    "Test MAE    :",
    round(
        best_advanced["Test MAE"],
        2
    )
)


# ============================================================
# 10. NAIVE BASELINE
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


print("\n" + "=" * 80)
print("NAIVE BASELINE")
print("=" * 80)

print(
    "R2  :",
    round(
        naive_r2,
        4
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
    "MAE :",
    round(
        naive_mae,
        2
    )
)


# ============================================================
# 11. SAVE RESULTS
# ============================================================

results_df.to_csv(
    "data/advanced_budget_model_results.csv",
    index=False
)


print(
    "\nResults saved to:"
)

print(
    "data/advanced_budget_model_results.csv"
)