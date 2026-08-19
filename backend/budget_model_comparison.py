import pandas as pd
import numpy as np
import time

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

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

data["week_end"] = pd.to_datetime(
    data["week_end"]
)

data = data.sort_values(
    "week_end"
).reset_index(drop=True)


# ============================================================
# 3. FEATURES AND TARGET
# ============================================================

features = [

    # Seasonal / calendar behaviour
    "week_sin",
    "week_cos",

    # Current known spending behaviour
    "current_week_spending",

    # Lag features
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


print("\n====================================")
print("CHRONOLOGICAL TRAIN-TEST SPLIT")
print("====================================")

print(
    "Training Samples:",
    len(X_train)
)

print(
    "Testing Samples:",
    len(X_test)
)


# ============================================================
# 5. MODELS
# ============================================================

models = {

    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=300,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}


# ============================================================
# 6. TRAIN AND EVALUATE
# ============================================================

results = []


print("\n====================================")
print("MODEL COMPARISON")
print("====================================")


for model_name, model in models.items():

    print(
        f"\nTraining: {model_name}"
    )

    start_time = time.time()


    model.fit(
        X_train,
        y_train
    )


    training_time = (
        time.time()
        - start_time
    )


    predictions = model.predict(
        X_test
    )


    mae = mean_absolute_error(
        y_test,
        predictions
    )


    mse = mean_squared_error(
        y_test,
        predictions
    )


    rmse = np.sqrt(
        mse
    )


    r2 = r2_score(
        y_test,
        predictions
    )


    results.append({

        "Model":
            model_name,

        "MAE":
            mae,

        "RMSE":
            rmse,

        "R2 Score":
            r2,

        "Training Time":
            training_time
    })


    print(
        "MAE:",
        round(
            mae,
            2
        )
    )


    print(
        "RMSE:",
        round(
            rmse,
            2
        )
    )


    print(
        "R2 Score:",
        round(
            r2,
            4
        )
    )


    print(
        "Training Time:",
        round(
            training_time,
            4
        ),
        "seconds"
    )


# ============================================================
# 7. MODEL RANKING
# ============================================================

comparison = pd.DataFrame(
    results
)


comparison = comparison.sort_values(
    by="R2 Score",
    ascending=False
).reset_index(
    drop=True
)


print("\n====================================")
print("FINAL MODEL RANKING")
print("====================================")


print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 8. BEST ADVANCED MODEL
# ============================================================

advanced_models = comparison[
    comparison["Model"]
    != "Linear Regression"
].reset_index(
    drop=True
)


best_advanced_model = (
    advanced_models.iloc[0]
)


print("\n====================================")
print("BEST ADVANCED MODEL")
print("====================================")


print(
    "Model:",
    best_advanced_model[
        "Model"
    ]
)


print(
    "R2 Score:",
    round(
        best_advanced_model[
            "R2 Score"
        ],
        4
    )
)


print(
    "RMSE:",
    round(
        best_advanced_model[
            "RMSE"
        ],
        2
    )
)


print(
    "MAE:",
    round(
        best_advanced_model[
            "MAE"
        ],
        2
    )
)


# ============================================================
# 9. BASELINE COMPARISON
# ============================================================

# Simple forecasting baseline:
# next week's spending = current week's spending

baseline_predictions = (
    X_test[
        "current_week_spending"
    ].values
)


baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)


baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)


baseline_r2 = r2_score(
    y_test,
    baseline_predictions
)


print("\n====================================")
print("NAIVE FORECAST BASELINE")
print("====================================")

print(
    "MAE:",
    round(
        baseline_mae,
        2
    )
)

print(
    "RMSE:",
    round(
        baseline_rmse,
        2
    )
)

print(
    "R2 Score:",
    round(
        baseline_r2,
        4
    )
)


# ============================================================
# 10. SAVE COMPARISON RESULTS
# ============================================================

comparison.to_csv(
    "data/budget_model_comparison.csv",
    index=False
)


print(
    "\nComparison Results Saved To:"
)

print(
    "data/budget_model_comparison.csv"
)