import pandas as pd
import numpy as np
import os
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. LOAD DATA
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
# 2. ADD IMPROVED TEMPORAL FEATURES
# ============================================================

# Additional lag features
data["lag_5"] = (
    data["weekly_spending"]
    .shift(5)
)

data["lag_6"] = (
    data["weekly_spending"]
    .shift(6)
)

data["lag_7"] = (
    data["weekly_spending"]
    .shift(7)
)

data["lag_8"] = (
    data["weekly_spending"]
    .shift(8)
)


# Rolling statistics
data["rolling_4_std"] = (
    data["weekly_spending"]
    .rolling(window=4)
    .std()
)

data["rolling_8_std"] = (
    data["weekly_spending"]
    .rolling(window=8)
    .std()
)


# Short-term trend
data["trend_2_week"] = (
    data["current_week_spending"]
    -
    data["spending_2_weeks_ago"]
)

data["trend_4_week"] = (
    data["current_week_spending"]
    -
    data["spending_4_weeks_ago"]
)


# Month seasonality
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


# Remove rows introduced by lagging
data = data.dropna().reset_index(
    drop=True
)


# ============================================================
# 3. FEATURES AND TARGET
# ============================================================

features = [

    # Current behaviour
    "current_week_spending",
    "current_transaction_count",
    "current_avg_transaction_amount",

    # Lags
    "spending_1_week_ago",
    "spending_2_weeks_ago",
    "spending_3_weeks_ago",
    "spending_4_weeks_ago",
    "lag_5",
    "lag_6",
    "lag_7",
    "lag_8",

    # Rolling averages
    "previous_2_week_avg",
    "previous_4_week_avg",
    "previous_8_week_avg",

    # Rolling volatility
    "rolling_4_std",
    "rolling_8_std",

    # Trend
    "spending_change",
    "spending_change_percentage",
    "trend_2_week",
    "trend_4_week",

    # Previous transaction behaviour
    "previous_transaction_count",
    "previous_avg_transaction_amount",

    # Seasonality
    "week_sin",
    "week_cos",
    "month_sin",
    "month_cos"
]


target = "next_week_spending"

X = data[features]
y = data[target]


# ============================================================
# 4. CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# ============================================================
# 5. MODELS
# ============================================================

models = {

    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=500,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=500,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=2,
        min_samples_split=4,
        min_samples_leaf=2,
        subsample=0.9,
        random_state=42
    ),

    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=10,
        l2_regularization=1.0,
        random_state=42
    )
}


# ============================================================
# 6. TRAIN + EVALUATE
# ============================================================

results = []
trained_models = {}


for model_name, model in models.items():

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
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

    r2 = r2_score(
        y_test,
        predictions
    )

    results.append({

        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2 Score": r2

    })

    trained_models[
        model_name
    ] = model


# ============================================================
# 7. NAIVE BASELINE
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

results.append({

    "Model": "Naive Forecast",
    "MAE": naive_mae,
    "RMSE": naive_rmse,
    "R2 Score": naive_r2

})


# ============================================================
# 8. RANK RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="R2 Score",
    ascending=False
).reset_index(drop=True)


print("\n" + "=" * 70)
print("FINAL BUDGET FORECASTING RANKING")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 9. SELECT BEST ADVANCED MODEL
# ============================================================

advanced_results = results_df[
    ~results_df["Model"].isin(
        [
            "Linear Regression",
            "Naive Forecast"
        ]
    )
].reset_index(drop=True)


best_advanced = advanced_results.iloc[0]

best_model_name = (
    best_advanced["Model"]
)


print("\n" + "=" * 70)
print("BEST ADVANCED MODEL")
print("=" * 70)

print(
    "Model:",
    best_model_name
)

print(
    "R2 Score:",
    round(
        best_advanced["R2 Score"],
        4
    )
)

print(
    "RMSE:",
    round(
        best_advanced["RMSE"],
        2
    )
)

print(
    "MAE:",
    round(
        best_advanced["MAE"],
        2
    )
)


# ============================================================
# 10. SAVE RESULTS
# ============================================================

results_df.to_csv(
    "data/final_budget_forecasting_results.csv",
    index=False
)


# ============================================================
# 11. SAVE BEST ADVANCED MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)

best_model = trained_models[
    best_model_name
]

joblib.dump(
    best_model,
    "models/final_budget_prediction_model.pkl"
)


print("\nFinal model saved to:")

print(
    "models/final_budget_prediction_model.pkl"
)

print(
    "\nResults saved to:"
)

print(
    "data/final_budget_forecasting_results.csv"
)