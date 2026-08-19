import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "data/budget_prediction_dataset.csv"

MODEL_PATH = (
    "models/final_gradient_boosting_budget_model.pkl"
)

FEATURE_PATH = (
    "models/final_budget_model_features.pkl"
)

OUTPUT_FOLDER = "graphs/budget_model"


# ============================================================
# 2. CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# 3. LOAD DATASET
# ============================================================

data = pd.read_csv(
    DATA_PATH
)

data["week_end"] = pd.to_datetime(
    data["week_end"]
)

data = data.sort_values(
    "week_end"
).reset_index(drop=True)


print("=" * 65)
print("BUDGET MODEL FINAL EVALUATION")
print("=" * 65)

print("\nDataset Loaded Successfully")
print("Dataset Shape:", data.shape)


# ============================================================
# 4. LOAD FINAL MODEL + FEATURES
# ============================================================

model = joblib.load(
    MODEL_PATH
)

features = joblib.load(
    FEATURE_PATH
)


print("\nFinal Gradient Boosting Model Loaded")
print("Number of Features:", len(features))


# ============================================================
# 5. PREPARE DATA
# ============================================================

X = data[features]

y = data[
    "next_week_spending"
]


# ============================================================
# 6. SAME CHRONOLOGICAL 80/20 SPLIT
# ============================================================

split_index = int(
    len(data) * 0.80
)


X_test = X.iloc[
    split_index:
]

y_test = y.iloc[
    split_index:
]

test_dates = data[
    "week_end"
].iloc[
    split_index:
]


print("\nTesting Samples:", len(X_test))


# ============================================================
# 7. MAKE PREDICTIONS
# ============================================================

predictions = model.predict(
    X_test
)


# ============================================================
# 8. FINAL PERFORMANCE METRICS
# ============================================================

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


print("\n" + "=" * 65)
print("FINAL TEST PERFORMANCE")
print("=" * 65)

print(
    "R2 Score:",
    round(r2, 4)
)

print(
    "MAE:",
    round(mae, 2)
)

print(
    "RMSE:",
    round(rmse, 2)
)


# ============================================================
# 9. ACTUAL VS PREDICTED DATA
# ============================================================

prediction_results = pd.DataFrame({

    "week_end":
        test_dates.values,

    "actual_spending":
        y_test.values,

    "predicted_spending":
        predictions
})


prediction_results[
    "absolute_error"
] = np.abs(

    prediction_results[
        "actual_spending"
    ]

    -

    prediction_results[
        "predicted_spending"
    ]
)


prediction_results.to_csv(

    "data/budget_actual_vs_predicted.csv",

    index=False
)


# ============================================================
# 10. GRAPH 1 — ACTUAL VS PREDICTED
# ============================================================

plt.figure(
    figsize=(12, 6)
)

plt.plot(
    prediction_results["week_end"],
    prediction_results["actual_spending"],
    marker="o",
    label="Actual Spending"
)

plt.plot(
    prediction_results["week_end"],
    prediction_results["predicted_spending"],
    marker="o",
    label="Predicted Spending"
)

plt.title(
    "Actual vs Predicted Weekly Spending"
)

plt.xlabel(
    "Week"
)

plt.ylabel(
    "Weekly Spending"
)

plt.xticks(
    rotation=45
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

actual_predicted_path = (
    f"{OUTPUT_FOLDER}/actual_vs_predicted.png"
)

plt.savefig(
    actual_predicted_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 11. CALCULATE RESIDUALS
# ============================================================

residuals = (
    y_test.values
    -
    predictions
)


# ============================================================
# 12. GRAPH 2 — RESIDUAL PLOT
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.scatter(
    predictions,
    residuals,
    alpha=0.75
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.title(
    "Residual Analysis of Budget Predictions"
)

plt.xlabel(
    "Predicted Weekly Spending"
)

plt.ylabel(
    "Residual (Actual - Predicted)"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

residual_path = (
    f"{OUTPUT_FOLDER}/residual_plot.png"
)

plt.savefig(
    residual_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 13. FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({

    "Feature":
        features,

    "Importance":
        model.feature_importances_
})


feature_importance = (
    feature_importance
    .sort_values(
        "Importance",
        ascending=False
    )
    .reset_index(drop=True)
)


feature_importance.to_csv(

    "data/budget_feature_importance.csv",

    index=False
)


print("\n" + "=" * 65)
print("TOP 10 IMPORTANT FEATURES")
print("=" * 65)

print(
    feature_importance
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# 14. GRAPH 3 — TOP FEATURE IMPORTANCE
# ============================================================

top_features = (
    feature_importance
    .head(10)
    .sort_values(
        "Importance",
        ascending=True
    )
)


plt.figure(
    figsize=(10, 7)
)

plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)

plt.title(
    "Top 10 Feature Importances - Gradient Boosting"
)

plt.xlabel(
    "Importance Score"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

feature_path = (
    f"{OUTPUT_FOLDER}/feature_importance.png"
)

plt.savefig(
    feature_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 15. COMPLETION SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 65)

print("\nGraphs Generated:")

print(
    "1.",
    actual_predicted_path
)

print(
    "2.",
    residual_path
)

print(
    "3.",
    feature_path
)


print("\nEvaluation Data Generated:")

print(
    "data/budget_actual_vs_predicted.csv"
)

print(
    "data/budget_feature_importance.csv"
)